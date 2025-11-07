from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from .models import Conversation, Message
from .serializers import ConversationSerializer
from .llm_client import generate_summary
from .vector_store import upsert_conversation, query_conversations
from .llm_client import generate_summary, generate_followup_questions

@api_view(["POST"])
def start_conversation(request):
    title = request.data.get("title", "New Conversation")
    conv = Conversation.objects.create(title=title)
    return Response({"conversation_id": conv.id})

@api_view(["POST"])
def send_message(request):
    from .llm_client import detect_intent, generate_summary, answer_knowledge_question, generate_followup_questions

    conv_id = request.data.get("conversation_id")
    user_text = request.data.get("message", "")

    if not conv_id or not user_text.strip():
        return Response({"error": "conversation_id and message are required"}, status=400)

    try:
        conv = Conversation.objects.get(id=conv_id)
    except Conversation.DoesNotExist:
        return Response({"error": "Conversation not found"}, status=404)

    Message.objects.create(conversation=conv, sender="user", content=user_text)

    if not conv.title or conv.title == "New Conversation":
        conv.title = _auto_title_from_message(user_text)
        conv.save(update_fields=["title"])

    intent = detect_intent(user_text)

    if intent == "summary":
        ai_text = generate_summary(user_text)
        follow_ups = []
    elif intent == "knowledge":
        ai_text = answer_knowledge_question(user_text)
        follow_ups = []
    else:
        ai_text = generate_summary(user_text)
        follow_ups = generate_followup_questions(ai_text)

    Message.objects.create(conversation=conv, sender="ai", content=ai_text)

    return Response({
        "reply": ai_text,
        "intent": intent,
        "follow_ups": follow_ups,
    })


def _auto_title_from_message(text: str) -> str:
    words = text.strip().split()
    base = " ".join(words[:6]) if words else "Untitled"
    return (base + ("…" if len(words) > 6 else "")).strip().title()


@api_view(["POST"])
def end_conversation(request):
    conv_id = request.data.get("conversation_id")
    if not conv_id:
        return Response({"error": "conversation_id is required"}, status=400)

    try:
        conv = Conversation.objects.get(id=conv_id)
    except Conversation.DoesNotExist:
        return Response({"error": "Conversation not found"}, status=404)

    messages = conv.messages.order_by("timestamp").values_list("sender", "content")
    full_chat_text = "\n".join([f"{s.upper()}: {c}" for s, c in messages])

    summary_prompt = f"Summarize this conversation in 4-6 bullet points:\n\n{full_chat_text}"
    summary = generate_summary(summary_prompt)

    conv.ai_summary = summary
    conv.end_time = timezone.now()
    conv.status = "ended"
    conv.save()

    upsert_conversation(
        conv.id,
        full_chat_text,  
        metadata={
            "title": conv.title or "Untitled",
            "summary": summary,
            "ended_at": conv.end_time.isoformat(),
        }
    )

    return Response({"summary": summary})

@api_view(["POST"])
def intelligent_query(request):
    question = request.data.get("question", "")
    if not question:
        return Response({"error": "Question is required"}, status=400)

    # Get top similar conversations from vector db
    results = query_conversations(question)
    docs = results.get("documents", [[]])[0]
    metadata = results.get("metadatas", [[]])[0]

    if not docs:
        return Response({"answer": "No relevant past conversations found."})

    # Construct context for the LLM 
    context = "\n\n".join([
        f"Title: {meta.get('title', 'No Title')}\nSummary: {meta.get('summary', '')}\nContent:\n{doc}"
        for doc, meta in zip(docs, metadata)
    ])

    prompt = f"Use the following context to answer the question:\n\n{context}\n\nQuestion: {question}"

    answer = generate_summary(prompt)

    return Response({
        "answer": answer,
        "sources": metadata
    })

@api_view(["GET"])
def list_conversations(request):
    qs = Conversation.objects.order_by("-start_time")
    data = ConversationSerializer(qs, many=True).data
    return Response(data)

@api_view(["GET"])
def get_conversation(request, pk):
    try:
        conv = Conversation.objects.get(pk=pk)
    except Conversation.DoesNotExist:
        return Response({"error": "Conversation not found"}, status=404)
    return Response(ConversationSerializer(conv).data)


@api_view(["PATCH"])
def edit_conversation_title(request, pk):
    new_title = request.data.get("title", "").strip()
    if not new_title:
        return Response({"error": "Title is required"}, status=400)

    try:
        conv = Conversation.objects.get(pk=pk)
    except Conversation.DoesNotExist:
        return Response({"error": "Conversation not found"}, status=404)

    conv.title = new_title
    conv.save(update_fields=["title"])
    return Response({"message": "Title updated", "id": conv.id, "new_title": new_title})


@api_view(["DELETE"])
def delete_conversation(request, pk):
    try:
        conv = Conversation.objects.get(pk=pk)
    except Conversation.DoesNotExist:
        return Response({"error": "Conversation not found"}, status=404)

    conv.delete()
    return Response({"message": "Conversation deleted", "id": pk})

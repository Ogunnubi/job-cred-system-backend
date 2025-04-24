from fastapi import APIRouter, Depends
from app.models.user import User
from app.schemas.user import UserOut
from app.schemas.chatGPT import AssistantRequest
from app.core.auth import get_current_user
from app.services.ai_service import get_ai_response

router = APIRouter()


@router.post("/assistant")
async def assistant_help(
        request: AssistantRequest,
        current_user: UserOut = Depends(get_current_user)
):
    prompt = request.message
    user_id = str(current_user.id)


    user = await User.get_by_id(current_user.id)
    user_context = f"User has {user.credits} credits available."

    system_prompt = """
        You are a helpful assistant for a job marketplace web application.
        Users can post jobs and apply to jobs using credits.
        """

    enhanced_prompt = f"{system_prompt}\n\n{user_context}\n\nUser question: {prompt}"

    response = await get_ai_response(enhanced_prompt, user_id)

    return {
        "message": response
    }
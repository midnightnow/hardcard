from fastapi import APIRouter
from pydantic import BaseModel
import random
import databutton as db

router = APIRouter()

class CompletionNudgeRequest(BaseModel):
    taskTitle: str
    taskDescription: str = ""
    daysStalled: int = 0

class CompletionNudgeResponse(BaseModel):
    message: str
    suggestion: str

@router.post("/completion-nudge")
def generate_completion_nudge(request: CompletionNudgeRequest) -> CompletionNudgeResponse:
    """
    Generates AI-powered nudges to help users complete stalled tasks based on the Cult of Done philosophy.
    """
    # Cult of Done inspired nudges
    nudges = [
        {
            "message": "Remember, banish procrastination!",
            "suggestion": "If you've waited more than a week on this task, it might be time to either finish it or let it go."
        },
        {
            "message": "Perfect is boring. Done is exciting!",
            "suggestion": "Laugh at perfection and just ship what you have now."
        },
        {
            "message": "Done is the engine of more.",
            "suggestion": "Completing this task will free you to start new exciting ones."
        },
        {
            "message": "Everything is a draft.",
            "suggestion": "Accept that this work is just a draft and it helps to get done."
        },
        {
            "message": "People without dirty hands are wrong.",
            "suggestion": "Stop planning and start doing - even a messy attempt is better than none."
        },
        {
            "message": "The point of being done is not to finish but to get other things done.",
            "suggestion": "Clear this from your plate so you can move on to other important tasks."
        },
    ]
    
    # Add day-specific nudges if the task has been stalled for a while
    if request.daysStalled > 3:
        nudges.append({
            "message": f"This task has been stalled for {request.daysStalled} days.",
            "suggestion": "Consider whether it's still worth pursuing or if it should be marked as failed and learned from."
        })
    
    if request.daysStalled > 7:
        nudges.append({
            "message": "A week has passed without action.",
            "suggestion": "The Cult of Done says: If you wait more than a week to get an idea done, abandon it."
        })
    
    # Return a random nudge
    selected_nudge = random.choice(nudges)
    return CompletionNudgeResponse(
        message=selected_nudge["message"],
        suggestion=selected_nudge["suggestion"]
    )

class TaskCompletionRequest(BaseModel):
    taskTitle: str
    projectTitle: str = ""
    difficultyLevel: int = 1 # 1-5

class TaskCompletionResponse(BaseModel):
    celebration: str
    rewardTitle: str
    rewardDescription: str
    bonusPoints: int

@router.post("/celebrate-completion")
def celebrate_task_completion(request: TaskCompletionRequest) -> TaskCompletionResponse:
    """
    Generates celebration messages and rewards for completed tasks to reinforce the Cult of Done philosophy.
    """
    # Base points based on difficulty
    base_points = request.difficultyLevel * 20
    
    # Celebrations
    celebrations = [
        "🎉 Amazing! Another one done!",
        "✅ Task complete! On to the next adventure!",
        "🚀 Done is the engine of more!",
        "⚡ You're unstoppable! Task completed!",
        "🏆 Completion achieved! Time to celebrate!",
        "💪 You did it! Progress unlocked!"
    ]
    
    # Reward types
    rewards = [
        {
            "title": "Speed Demon",
            "description": "You're making progress at lightning speed.",
            "bonus": 10
        },
        {
            "title": "Productivity Master",
            "description": "Your commitment to getting things done is inspiring.",
            "bonus": 15
        },
        {
            "title": "Momentum Builder",
            "description": "You're building an unstoppable force of productivity.",
            "bonus": 12
        },
        {
            "title": "Done Crusader",
            "description": "A true believer in the Cult of Done philosophy.",
            "bonus": 25
        },
        {
            "title": "Perfection Slayer",
            "description": "You've laughed at perfection and chosen completion instead.",
            "bonus": 20
        },
    ]
    
    selected_celebration = random.choice(celebrations)
    selected_reward = random.choice(rewards)
    total_points = base_points + selected_reward["bonus"]
    
    return TaskCompletionResponse(
        celebration=selected_celebration,
        rewardTitle=selected_reward["title"],
        rewardDescription=selected_reward["description"],
        bonusPoints=total_points
    )

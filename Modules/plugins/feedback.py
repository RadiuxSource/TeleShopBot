from pyrogram import filters
from Modules import zenova, MSG_GROUP

@zenova.on_message(filters.command("feedback"))
async def feedback(client, message):
    await message.reply_text("Please enter your feedback now:")
    feedback_msg = await client.listen(
    chat_id=message.chat.id, 
    user_id=message.from_user.id
    )
    feedback_text = feedback_msg.text
    try:
        if feedback_text:
            user_info = f"User ID: {message.from_user.id}\nUsername: @{message.from_user.username}"
            feedback_info = (
                f"📣 New Feedback! 📣\n\n{user_info}\n\nFeedback: {feedback_text}"
            )
            await client.send_message(MSG_GROUP, feedback_info)
            await message.reply_text("Thanks for your feedback! It has been sent to the team.")
        else:
            await message.reply_text("Your feedback message cannot be empty. Please try again.")
    except Exception as e:
        try:
            await client.send_message(MSG_GROUP, e)
        except:
            print(f"An error caught during sending feedback to log channel!! Please chack log channel id properly. Error:{e}")

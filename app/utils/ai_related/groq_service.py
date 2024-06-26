import re
from app.utils.ai_related.prompt_templates import basic_prompt, history_prompt
from app.utils.logger import logger

class GroqService:
    def __init__(self, ):
        self.basic_prompt = basic_prompt
        self.history_prompt = history_prompt

    async def ask_question(self, author, author_id, user_message):
        try:
            # Gluing discord username to the message
            logger.info(f"Question: {user_message}")
            messages = [
                {"role": "system", "content": basic_prompt},
                {"role": "user", "content": f"{author} ({author_id}): {user_message}"},
            ]
            #logger.debug(f"Messages: {messages}")
            return messages
        except Exception as ex:
            logger.error(f"Error in ask_question: {ex}")
            return "Sorry, something went wrong while processing your request."
        
    async def assemble_chat_history(self, context):
        try:
            messages = [message async for message in context.channel.history(limit=30)]

            chat_messages = []
            previous_author = None
            previous_author_id = None
            concatenated_content = ""

            for message in reversed(messages):
                author = message.author
                current_author = author.name
                author_id = message.author.id

                if current_author == previous_author:
                    concatenated_content += "\n" + message.content
                else:
                    if concatenated_content:
                        chat_messages.append({
                            "role": "assistant" if previous_author in ["AI-Chan"] else "user",
                            "content": f"{previous_author} ({previous_author_id}): {concatenated_content}"
                        })

                    previous_author = current_author
                    previous_author_id = author_id
                    concatenated_content = message.content

            # Add the last concatenated message
            if concatenated_content:
                chat_messages.append({
                    "role": "assistant" if previous_author in ["AI-Chan"] else "user",
                    "content": f"{previous_author} ({previous_author_id}): {concatenated_content}"
                })

            # Insert the basic prompt and history prompt at the beginning
            chat_messages.insert(0, {"role": "system", "content": self.basic_prompt})
            chat_messages.insert(1, {"role": "system", "content": self.history_prompt})

            return chat_messages

        except Exception as ex:
            logger.exception("Error in assemble_chat_history")
            raise

    async def add_command_messages(self, ctx, chat_messages, user_message):

        chat_messages.append({
            "role": "user",
            "content": "That was all history. Take a deep breath, relax a little. "
                    "Think about the history you just got. To mention someone, use their ID like this: <@user_id>. "
                    "Using this knowledge, try to answer the next question as best as you can."
        })
        chat_messages.append({
            "role": "user",
            "content": f"{ctx.author.name} ({ctx.author.id}): {user_message}"
        })
        return chat_messages



    # async def say_good_morning(self, channel_id):
    #     try:
    #         channel = self.bot.get_channel(channel_id)
    #         if channel:
    #             context = await channel.history(limit=30).flatten()
    #             if context:
    #                 chat_history = await self.groq_service.assemble_chat_history(context[0])
    #                 messages = self.groq_service.add_command_messages(chat_history, "Good morning, everyone!", context[0].author)
    #                 additional_message = {
    #                     "role": "user",
    #                     "content": "Now, you're using a function that triggers every morning. Say good morning to everyone, "
    #                             "you can use history to maybe ask about some stuff that transpired before, be funny."
    #                 }
    #                 messages.append(additional_message)
    #                 response, prompt_tokens, completion_tokens, total_tokens = self.groq_service.send_to_groq(messages)
    #                 await channel.send(response)
    #     except Exception as ex:
    #         logger.error(f"Error in say_good_morning: {ex}")




    def remove_special_chars(self, input):
        return re.sub(r'[^0-9a-zA-Z]', '', input)


    
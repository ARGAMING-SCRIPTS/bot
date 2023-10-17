from telethon.sync import TelegramClient, events
import requests
import json
import uuid
import html

api_id = '15990002'
api_hash = 'f573697ac99202b70e530904df73597a'
client = TelegramClient('my_session', api_id, api_hash)
group_id = -1001733036673
user_info = {}

@client.on(events.NewMessage)
async def handle_message(event):
    user_message = event.text
    chat_id = event.chat_id

    if user_message.lower() == '/start':
        if await is_user_in_group(chat_id, group_id):
            await event.reply("Welcome! You can register your ARGAMING SCRIPTS services account here. Type /register to start registration process.")
        else:
            await event.reply("Failed to synchronize with the server.")
    elif user_message.lower() == '/register':
        if await is_user_in_group(chat_id, group_id):
            await event.reply("Username:")
            user_info[chat_id] = {"step": 1}
        else:
            await event.reply("Failed to synchronize with the server.")
    else:
        if chat_id in user_info:
            step = user_info[chat_id]["step"]
            if step == 1:
                user_info[chat_id]["username"] = user_message
                user_info[chat_id]["step"] = 2
                await event.reply("Password:")
            elif step == 2:
                user_info[chat_id]["password"] = user_message
                user_info[chat_id]["step"] = 3
                await event.reply("Birthday:")
            elif step == 3:
                user_info[chat_id]["birthday"] = user_message
                user_info[chat_id]["step"] = 4
                user_info[chat_id]["uuid"] = str(uuid.uuid4())
                try:
                    user = await client.get_entity(chat_id)
                    if user.username:
                        user_info[chat_id]["telegram_username"] = user.username
                    else:
                        user_info[chat_id]["telegram_username"] = user.first_name
                except Exception as e:
                    print(f"Error getting Telegram username or name: {str(e)}")

                await send_info_to_server(chat_id)
        else:
            pass

async def is_user_in_group(user_id, group_id):
    try:
        async for user in client.iter_participants(group_id):
            if user.id == user_id:
                return True
        return False

    except Exception as e:
        print(f"Error checking if user is in the group: {str(e)}")
        return False

async def send_info_to_server(chat_id):
    try:
        # Construct the JSON data
        user_data = {
            "Register": {
                "Username": user_info[chat_id]["username"],
                "Password": user_info[chat_id]["password"],
                "Birthday": user_info[chat_id]["birthday"],
                "UUID": user_info[chat_id]["uuid"],
                "TelegramUsername": user_info[chat_id]["telegram_username"]
            }
        }

        # Convert the data to JSON format
        json_data = json.dumps(user_data)

        # Define your server's endpoint URL
        server_url = "https://argamingscriptss.000webhostapp.com/AccountInfo.php"

        # Send the JSON data to the server using POST request
        response = requests.post(server_url, data=json_data, headers={'Content-Type': 'application/json'})

        # Check if the registration was successful
        response_data = response.json()
        if 'msg' in response_data:
            # Registration was successful
            success_message = response_data['msg']
            # Replace '<br>' with newline characters
            success_message = success_message.replace('<br>', '\n')
            await client.send_message(chat_id, success_message)
        elif 'err_msg' in response_data:
            # Registration failed
            await client.send_message(chat_id, f"Failed to register: {response_data['err_msg']}")


    except Exception as e:
        # Handle any exceptions that may occur during the process
        print(f"Failed to retrieve server response: {str(e)}")


# Start the client
client.start()
client.run_until_disconnected()
              

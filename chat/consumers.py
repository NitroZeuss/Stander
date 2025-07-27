import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from users.models import Message  # Your DB model for optional storage


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        # This is the channel group that all users will join
        # It can be dynamic (like per-room), but here it's hardcoded
        self.group_name = 'chat_group'

        # Add this socket/channel connection to the group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name  # unique ID Django Channels gives this socket
        )

        self.accept()  # Accept the WebSocket connection

        # Send welcome message when connection is established
        self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': (
                f"Welcome {self.scope['user']}!" 
                if self.scope["user"].is_authenticated 
                else "Welcome anonymous user!"
            )
        }))

    def disconnect(self, close_code):
        # When socket is closed, remove it from the group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data):
        # This runs when frontend sends a message via WebSocket
        data = json.loads(text_data)  # decode the JSON message from frontend
        message = data['message']     # grab the actual text
        persist = data.get("persist", False)  # 🔥 check if it should be saved

        # Get username — fall back to "anon" if not logged in
        username = (
            self.scope["user"].username 
            if self.scope["user"].is_authenticated 
            else "anon"
        )

        # 👇 Send message to all users in the group (broadcast)
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'chat_message',  # this triggers the method below
                'message': message,
                'username': username
            }
        )

        # 💾 Optional: Save to DB only if persist = true
        if persist:
            Message.objects.create(
                user=self.scope["user"] 
                    if self.scope["user"].is_authenticated 
                    else None,
                content=message
            )

    def chat_message(self, event):
        # This method is called when a group message is received
        # 'event' is the dictionary we sent above in group_send()
        message = event['message']
        username = event['username']

        # Send the message back to the client (broadcast to all sockets)
        self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username
        }))

from nio import SyncError, SyncResponse, MatrixRoom, RoomMessageText

from im_api.core.context import Context
from im_api.models.message import Message, Channel, User
from im_api.models.platform import Platform

homeserver_online = True

def on_sync_error(self, response: SyncError):
    global homeserver_online
    self.logger.error(f"Sync error in matrix: {response.status_code}")
    if response.status_code >= 500:
        homeserver_online = False

def on_sync_response(self, response: SyncResponse):
    self.logger.info(response.next_batch)

def textmsg_callback(self, room: MatrixRoom, event: RoomMessageText) -> None:
    print(f"[{room.display_name}] <{room.user_name(event.sender)}> {event.body}")
    message = Message(
        id=event.event_id,
        content=event.body,
        channel=Channel(
            id=room.room_id,
            type="group",
            name=room.display_name
        ),
        user=User(
            id=event.sender,
            name=self.client.get_displayname(event.sender),
            nick=room.user_name(event.sender),
            avatar=self.client.get_avatar(event.sender)
        ),
        platform=Platform.MATRIX
    )

    if self.message_callback:
        self.message_callback(Platform.MATRIX, message)
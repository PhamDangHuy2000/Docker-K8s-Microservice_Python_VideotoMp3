import json
import pika


def upload_video(file_to_upload, fs, channel, access, server):
    try:
        file_id = fs.put(file_to_upload)
    except Exception as e:
        server.logger.info(e)
        return "Internal server error", 500

    # dat mot tin nhan vao hang doi de dich vu chuyen doi xuooi dong
    # sau do co the sd tin nhan do
    message = {
        "video_file_id": str(file_id),
        "mp3_file_id": None,
        "username": access["username"],
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                # duy tri cac tin nhan trong hang doi trong truong hop xay ra su co/khoidonglai
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
    except Exception as e:
        server.logger.info(e)
        # delete the file from the DB, because if the message
        # fails to be sent to the queue, the file will never be
        # processed and wil end up with a lots of stalled files
        fs.delete(file_id)
        return "Internal server error", 500

import os
import json
import tempfile

import pika
from bson.objectid import ObjectId
from moviepy.editor import VideoFileClip


def start_conversion(message, fs_videos, fs_mp3s, channel):
    message = json.loads(message)

    # lấy nội dung video từ MongoDB và đặt chúng vào một tệp tạm thời
    video_content = fs_videos.get(ObjectId(message["video_file_id"]))
    temp_file = tempfile.NamedTemporaryFile()
    temp_file.write(video_content.read())

    # tạo âm thanh từ file video
    audio = VideoFileClip(temp_file.name).audio
    temp_file.close()   # tự động xóa tập tin

    # ghi âm thanh vào một tập tin tạm thời
    temp_file_path = tempfile.gettempdir() + f"/{message['video_file_id']}.mp3"
    audio.write_audiofile(temp_file_path)

    # lưu trữ âm thanh trong MongoDB
    file_handler = open(temp_file_path, "rb")
    audio_data = file_handler.read()
    file_id = fs_mp3s.put(audio_data)
    # không tự động bị xóa vì nó không được tạo bằng mô-đun tempfile
    file_handler.close()
    os.remove(temp_file_path)

    # cập nhật tin nhắn và gửi nó đến hàng đợi MP3
    message["mp3_file_id"] = str(file_id)
    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                # duy trì các tin nhắn trong hàng đợi trong trường hợp xảy ra sự cố/khởi động lại nhóm
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
    except Exception as e:
        print(e)
        # xóa tệp khỏi MongoDB vì nó sẽ không bao giờ được xử lý
        # nếu tin nhắn không được gửi vào hàng đợi
        fs_mp3s.delete(file_id)
        return "Failed to publish message"

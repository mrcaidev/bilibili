# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import requests
import os
import subprocess

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62',
    'referer': 'https://www.bilibili.com/'
}


class BilibiliPipeline:

    translate_dict = {}

    def process_item(self, item, spider):
        # Unpack the item passed in.
        name = item['name']
        page = item['page']
        audio_url = item['audio_url']
        video_url = item['video_url']

        # Store original name in case it may be illegal. (\/:*?<>| or spaces)
        self.translate_dict[f'{page}'] = name

        # Create cache directory if it does not exist.
        if not os.path.exists('cache'):
            os.mkdir('cache')

        # Store audio and video grouped by the name of that part.
        cur_dir = os.path.join('cache', str(page))
        if not os.path.exists(cur_dir):
            os.mkdir(cur_dir)

        # Prompt.
        print(f'Downloading {name}')

        # Write files.
        with open(os.path.join(cur_dir, f'{page}.mp3'), 'wb') as fw:
            fw.write(requests.get(url=audio_url, headers=headers).content)
        with open(os.path.join(cur_dir, f'{page}.mp4'), 'wb') as fw:
            fw.write(requests.get(url=video_url, headers=headers).content)

        return item

    def close_spider(self, spider):
        # Create output directory if it does not exist.
        if not os.path.exists('output'):
            os.mkdir('output')

        # For each part in cache:
        for part_num in os.listdir('cache'):
            # Get the paths of audio and video file.
            cur_dir = os.path.join('cache', part_num)
            audio, video = os.listdir(cur_dir)
            audio = os.path.join(cur_dir, audio)
            video = os.path.join(cur_dir, video)

            # Get the path of output file.
            output = os.path.join('output', f'{part_num}.mp4')

            # Merge audio and video into output file.
            subprocess.call(
                f'ffmpeg -i {audio} -i {video} -c:v copy -c:a aac -strict experimental {output}', shell=True)

            # Remove the part directory and its content.
            os.remove(audio)
            os.remove(video)
            os.rmdir(cur_dir)

            # Rename the output video with its original name.
            original_name = self.translate_dict[f'{part_num}']
            os.rename(output, f'{os.path.join("output", original_name)}.mp4')

        # Remove cache directory.
        os.rmdir('cache')

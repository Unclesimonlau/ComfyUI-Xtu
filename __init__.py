import os
import torchaudio
import torch
import folder_paths
import io
import json
import struct
import random
import requests
from .node.xstutts import *
from .node.split import *
from .node.cstxt import *
from .tools.i18n.i18n import I18nAuto

NODE_CLASS_MAPPINGS = {
    "xstu": Xstu_tts,
    "xstu_tuiwen": Xstu_tts_tuiwen,
    "srow": srow,
    "Example": srowtostring,
    "cstxt": txt_input,
    "txt_len": txt_len,
    "fenkuai": fenkuai,
    "autotext": autotext,
    "Text2AutioEdgeTts": mirco_2_audio,
    "novel_draft": create_draf,
    "novel_draft_2": sc_cao_gao,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "xstu": "🐅XSTU TXT GPTSo语音合成",
    "xstu_tuiwen": "🐅XSTU TXT GPTSo语音合成推文版",
    "srow": "🐅XSTU SROW 按行分割",
    "Example": "🐅XSTU SROW to String 按行分割 to String Node",
    "cstxt": "🐅XSTU TXT PATH 文本输入",
    "txt_len": "🐅XSTU TXT to length 文本 to length",
    "fenkuai": "🐅XSTU SQUN 按标点分割",
    "autotext": "🐅XSTU TXT AI 自动统计",
    "Text2AutioEdgeTts": "🐅XSTU MircoTTS 微软文本转语音",
    "novel_draft": "🐅XSTU CapCut Name 剪映项目名",
    "novel_draft_2": "🐅XSTU CapCut Save 保存剪映草稿",
}

all = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
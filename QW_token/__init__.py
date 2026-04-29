import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from access_token_all import wx_token_mgr
from send_notice import send_template_card

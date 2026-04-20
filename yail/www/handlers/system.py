# -*- coding: utf-8 -*-
from lib.yeab.web import post, ResponseBody
from conf.dev import ENABLE_BATCH_IMPORT


@post("/system/config")
@ResponseBody
async def get_system_config(request):
    return {
        "enableBatchImport": ENABLE_BATCH_IMPORT
    }

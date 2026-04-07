---
title: Test Space
sdk: gradio
app_file: app.py
---

import gradio as gr

def hello(name):
    return "Hello " + name + "!"

iface = gr.Interface(fn=hello, inputs="text", outputs="text")

if __name__ == "__main__":
    iface.launch()

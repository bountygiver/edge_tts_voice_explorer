import tkinter
from tkinter import ttk
import edge_tts
import asyncio
import tempfile
import vlc

root = tkinter.Tk()
language_selected = tkinter.StringVar()
voice_selected = tkinter.StringVar()
test_text = tkinter.StringVar()
voice_result = tkinter.StringVar()
language_list = []
voices = []
voice_list = ["Please select a language"]
voice_list_var = tkinter.StringVar(value=voice_list)

async def initialization():
    global language_list, voices
    voices = await edge_tts.list_voices()
    language_list = list(set([v["FriendlyName"].split(" - ")[1] for v in voices]))
    language_list.sort()

asyncio.run(initialization())

tempfolder = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)

if __name__ == '__main__':
    root.title("Edge TTS voice explorer")
    root.geometry("640x480")
    tkinter.Grid.rowconfigure(root, 0, weight=1)
    tkinter.Grid.columnconfigure(root, 0, weight=1)
    rootFrame = ttk.Frame(root, padding=10)
    rootFrame.grid(column=0, row=0, sticky=tkinter.N+tkinter.S+tkinter.E+tkinter.W)
    rootFrame.columnconfigure(0, weight=1)
    rootFrame.rowconfigure(2, weight=1)

    ttk.Label(rootFrame, text="Select a voice").grid(column=0, row=0, sticky=tkinter.N+tkinter.E+tkinter.W)
    langaugeWidget = ttk.Combobox(rootFrame, values=language_list, textvariable=language_selected)
    langaugeWidget.grid(column=0, row=1, sticky=tkinter.N+tkinter.E+tkinter.W)
    voiceFrame = ttk.Frame(rootFrame)
    voiceFrame.grid(column=0, row=2, pady= 3, sticky=tkinter.N+tkinter.S+tkinter.E+tkinter.W)
    voiceScroll = tkinter.Scrollbar(voiceFrame, orient="vertical")
    voiceScroll.grid(column=1, row=0, sticky=tkinter.N+tkinter.S+tkinter.W)
    voiceList = tkinter.Listbox(voiceFrame, selectmode="single", listvariable=voice_list_var, yscrollcommand=voiceScroll.set)
    voiceScroll.config(command=voiceList.yview)
    voiceList.grid(column=0, row=0, sticky=tkinter.N+tkinter.S+tkinter.E+tkinter.W)
    testText = ttk.Entry(rootFrame, textvariable=test_text)
    testText.grid(column=0, row=3, sticky=tkinter.S+tkinter.E+tkinter.W)
    def speakVoice():
        voice = [v["ShortName"] for v in voices if v["FriendlyName"] == voiceList.selection_get()]
        if voice and len(voice) > 0:
            communicate = edge_tts.Communicate(test_text.get(), voice[0])
            file = tempfile.NamedTemporaryFile(dir=tempfolder.name, suffix=".mp3", delete=False)
            with (
                open(file.name, "wb")
            ) as audio_file:
                for chunk in communicate.stream_sync():
                    if chunk["type"] == "audio":
                        audio_file.write(chunk["data"])
            p = vlc.MediaPlayer(file.name)
            p.play()
    playText = ttk.Button(rootFrame, text="Play", command=speakVoice)
    playText.grid(column=0, row=4, sticky=tkinter.S+tkinter.E+tkinter.W)
    ttk.Label(textvariable=voice_result).grid(column=0, row=5, sticky=tkinter.S+tkinter.E+tkinter.W)
    rootFrame.rowconfigure(2, weight=1)
    voiceFrame.rowconfigure(0, weight=1)
    voiceFrame.columnconfigure(0, weight=1)

    def comboSelected(event):
        voice_list_var.set([v["FriendlyName"] for v in voices if v["FriendlyName"].split(" - ")[1] == language_selected.get()])

    def voiceSelected(event):
        voice = [v for v in voices if v["FriendlyName"] == voiceList.selection_get()]
        if voice and len(voice) > 0:
            locale = voice[0]["Locale"].split('-')[0].lower()[:2]
            voice_matches = [f for f in voices if f["Locale"].split('-')[0].lower().startswith(locale)]
            voice_result.set(f"Use !v{locale}{voice_matches.index(voice[0]) + 1}")

    langaugeWidget.bind("<<ComboboxSelected>>", comboSelected)
    voiceList.bind("<<ListboxSelect>>", voiceSelected)
    root.mainloop()
    tempfolder.cleanup()

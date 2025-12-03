
# if you dont use pipenv uncomment the following:
# from dotenv import load_dotenv
# load_dotenv()

#VoiceBot UI with Gradio

import os
import gradio as gr

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import record_audio, transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts, text_to_speech_with_elevenlabs

#load_dotenv()

system_prompt="""Act as a warm reassuring yet professional medical doctor who is a general specialist capable of shifting into any specialty based on what the uploaded image suggests and analyze the medical image provided by the user with what you see by directly stating what condition you think the person may have without using any numbers special characters or phrases like in the image I see and provide a concise medical impression expressed in one long paragraph containing exactly two sentences while speaking naturally as if addressing a real patient and include possible differential diagnoses even if the image appears normal and then gently suggest appropriate remedies along with the names of the medicines and clearly mention their active constituents in simple accurate terms while keeping the explanation brief and patient friendly without giving any warnings disclaimers or AI style phrasing.

            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""


def process_inputs(audio_filepath, image_filepath):
    speech_to_text_output = transcribe_with_groq(GROQ_API_KEY=os.environ.get("GROQ_API_KEY"), 
                                                 audio_filepath=audio_filepath,
                                                 stt_model="whisper-large-v3")

    # Handle the image input
    if image_filepath:
        doctor_response = analyze_image_with_query(query=system_prompt+speech_to_text_output, encoded_image=encode_image(image_filepath), model="meta-llama/llama-4-scout-17b-16e-instruct") #model="meta-llama/llama-4-maverick-17b-128e-instruct") 
    else:
        doctor_response = "No image provided for me to analyze"

    voice_of_doctor = text_to_speech_with_elevenlabs(input_text=doctor_response, output_filepath="final.mp3") 

    return speech_to_text_output, doctor_response, voice_of_doctor


# Create the interface
iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath"),
        gr.Image(type="filepath")
    ],
    outputs=[
        gr.Textbox(label="Speech to Text"),
        gr.Textbox(label="Doctor's Response"),
        gr.Audio("Temp.mp3")
    ],
    title="AI Doctor with Vision and Voice"
)

iface.launch(debug=True)

#http://127.0.0.1:7860

# now this is similar to above code only. just that clear button is removed and now doctor voice can also be played in UI itself along with attachment file is generated. 
'''
import os
import gradio as gr

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts, text_to_speech_with_elevenlabs

system_prompt = """You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""

def process_inputs(audio_filepath, image_filepath):
    # Debug: Check if audio is captured
    print(f"Audio file received: {audio_filepath}")
    print(f"Image file received: {image_filepath}")
    
    # Handle audio input
    if audio_filepath is None:
        speech_to_text_output = "No audio recorded"
    else:
        try:
            speech_to_text_output = transcribe_with_groq(
                GROQ_API_KEY=os.environ.get("GROQ_API_KEY"), 
                audio_filepath=audio_filepath,
                stt_model="whisper-large-v3"
            )
        except Exception as e:
            speech_to_text_output = f"Error in transcription: {str(e)}"

    # Handle the image input
    if image_filepath:
        try:
            doctor_response = analyze_image_with_query(
                query=system_prompt + speech_to_text_output, 
                encoded_image=encode_image(image_filepath), 
                model="meta-llama/llama-4-scout-17b-16e-instruct"
            )
        except Exception as e:
            doctor_response = f"Error in image analysis: {str(e)}"
    else:
        doctor_response = "No image provided for me to analyze"

    # Generate voice response
    try:
        audio_output_path = "final_response.mp3"
        text_to_speech_with_elevenlabs(
            input_text=doctor_response, 
            output_filepath=audio_output_path
        )
        voice_of_doctor = audio_output_path
    except Exception as e:
        voice_of_doctor = None
        print(f"Error in TTS: {str(e)}")

    return speech_to_text_output, doctor_response, voice_of_doctor

# Create the interface
iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(
            sources=["microphone"], 
            type="filepath",
            format="wav",
            label="🎤 Record Your Voice"
        ),
        gr.Image(
            type="filepath",
            label="📷 Upload Medical Image"
        )
    ],
    outputs=[
        gr.Textbox(label="🗣️ Speech to Text"),
        gr.Textbox(label="👨‍⚕️ Doctor's Response"),
        gr.Audio(label="🔊 Doctor's Voice Response")
    ],
    title="🏥 AI Doctor with Vision and Voice",
    description="Record your voice and upload an image for medical analysis"
)

iface.launch(debug=True)
'''




#Generated by claude. where in 
'''Separated recording from processing - Audio recording is now independent
Added explicit submit button - Processing only happens when you click "Analyze"
Added max_threads=10 - Allows concurrent operations
Removed automatic processing - Audio recording won't trigger processing

The root cause was likely that your original gr.Interface was trying to process the audio immediately when it was recorded, causing the server to be busy and interfering with the recording process.
Alternative quick fix for your original code:
Change your gr.Interface to process only on submit, not on input change:'''


'''
import os
import gradio as gr
from concurrent.futures import ThreadPoolExecutor
import threading

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts, text_to_speech_with_elevenlabs

system_prompt = """You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""

def process_inputs(audio_filepath, image_filepath):
    # Debug: Check if audio is captured
    print(f"Audio file received: {audio_filepath}")
    print(f"Image file received: {image_filepath}")
    
    # Handle audio input
    if audio_filepath is None:
        speech_to_text_output = "No audio recorded"
    else:
        try:
            speech_to_text_output = transcribe_with_groq(
                GROQ_API_KEY=os.environ.get("GROQ_API_KEY"), 
                audio_filepath=audio_filepath,
                stt_model="whisper-large-v3"
            )
        except Exception as e:
            speech_to_text_output = f"Error in transcription: {str(e)}"

    # Handle the image input
    if image_filepath:
        try:
            doctor_response = analyze_image_with_query(
                query=system_prompt + speech_to_text_output, 
                encoded_image=encode_image(image_filepath), 
                model="meta-llama/llama-4-scout-17b-16e-instruct"
            )
        except Exception as e:
            doctor_response = f"Error in image analysis: {str(e)}"
    else:
        doctor_response = "No image provided for me to analyze"

    # Generate voice response
    try:
        audio_output_path = "final_response.mp3"
        text_to_speech_with_elevenlabs(
            input_text=doctor_response, 
            output_filepath=audio_output_path
        )
        voice_of_doctor = audio_output_path
    except Exception as e:
        voice_of_doctor = None
        print(f"Error in TTS: {str(e)}")

    return speech_to_text_output, doctor_response, voice_of_doctor

# Create interface with separated recording and processing
with gr.Blocks(title="AI Doctor with Vision and Voice") as iface:
    gr.Markdown("# 🏥 AI Doctor with Vision and Voice")
    gr.Markdown("Record your voice and upload an image for medical analysis")
    
    with gr.Row():
        with gr.Column():
            # Audio recording - separated from processing
            audio_input = gr.Audio(
                sources=["microphone"], 
                type="filepath",
                label="🎤 Record Your Voice"
            )
            
            image_input = gr.Image(
                type="filepath",
                label="📷 Upload Medical Image"
            )
            
            # Separate submit button
            submit_btn = gr.Button("🔍 Analyze", variant="primary")
        
        with gr.Column():
            speech_output = gr.Textbox(label="🗣️ Speech to Text")
            doctor_output = gr.Textbox(label="👨‍⚕️ Doctor's Response")
            voice_output = gr.Audio(label="🔊 Doctor's Voice Response")
    
    # Only process when submit is clicked, not when audio changes
    submit_btn.click(
        fn=process_inputs,
        inputs=[audio_input, image_input],
        outputs=[speech_output, doctor_output, voice_output]
    )

# Launch with specific settings to avoid blocking
iface.launch(
    debug=True,
    show_error=True,
    server_name="127.0.0.1",
    server_port=7860,
    max_threads=10  # Allow multiple concurrent requests
)
iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(
            sources=["microphone"], 
            type="filepath",
            format="wav",
            label="🎤 Record Your Voice"
        ),
        gr.Image(
            type="filepath",
            label="📷 Upload Medical Image"
        )
    ],
    outputs=[
        gr.Textbox(label="🗣️ Speech to Text"),
        gr.Textbox(label="👨‍⚕️ Doctor's Response"),
        gr.Audio(label="🔊 Doctor's Voice Response")
    ],
    live=False,
    title="🏥 AI Doctor with Vision and Voice",
    description="Record your voice and upload an image for medical analysis"
)

iface.launch(debug=True)
'''

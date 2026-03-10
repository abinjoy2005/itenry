"""
Travel planner based on Agentic AI workflow.

This module deploys a portal which can customize a day to day travel itinerary
for a person using multiple specialized AI crews.

Implemented using Sambanova Cloud, Gradio and Crew AI.
A deployment is available at https://huggingface.co/spaces/sambanovasystems/trip-planner
"""

import datetime
import json
import logging
from typing import List, Tuple

import gradio as gr
import plotly.graph_objects as go
import os
import openai

from crew import AddressSummaryCrew, TravelCrew
from db import log_query
from fpdf import FPDF

client = openai.OpenAI(
    api_key=os.environ.get("SAMBANOVA_API_KEY"),
    base_url="https://api.sambanova.ai/v1",
)

def start_chat(context):
    return gr.Chatbot(visible=True), gr.Textbox(visible=True), context

def respond(message, chat_history, context, model="Meta-Llama-3.1-70B-Instruct"):
    # Simple response incorporating context
    response = client.chat.completions.create(
                   model=model,
                   messages=[{"role":"system",
                              "content":"You are a helpful assistant"},
                             {"role": "user",
                              "content": "Here is a trip itinerary: %s. Please answer the specific question asked by the user. %s " % (message, context)}],
                   temperature=0.1,
                   top_p=0.1
                )
    result = response.choices[0].message.content
    bot_message = result
    chat_history.append((message, bot_message))
    return "", chat_history

def export_pdf(input_text:str, input_chat:str):
    """
    Create a downloadable pdf for the given input text

    Args:
         input_text: The text that needs to be made a pdf
         input_chat: Chat messages

    Result:
         Downloadable pdf
    """
    current_datetime = datetime.datetime.now()
    # Format the current date and time as YYYY-MM-DD_HH-MM-SS
    datetime_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    file_name = "itinerary_%s.pdf" % datetime_str
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)

    for line in input_text.split('\n'):
        clean_line = line.strip()
        if clean_line.startswith('**'):
            pdf.set_font("Arial", size=12, style='B')
            pdf.multi_cell(0, 5, clean_line[2:].lstrip()[:-2].rstrip())
            pdf.set_font("Arial", size=12, style='')
        else:
            pdf.multi_cell(0, 5, clean_line)

    pdf.ln()
    for conversation in input_chat:
        counter = 0
        for line in conversation:
            clean_line = line.strip()
            if clean_line:
                if counter == 0:
                    pdf.ln()
                    pdf.set_font("Arial", size=12, style='I')
                    counter += 1
                else:
                    pdf.set_font("Arial", size=12, style='')
                pdf.multi_cell(0, 5, clean_line)

    pdf.output(file_name).encode('latin-1')
    return file_name

def filter_map(text_list: List[str], lat: List[str], lon: List[str]) -> go.Figure:
    """
    Create a Map showing the points specified in the inputs.

    Args:
        text_list: List of the description of all locations that will be shown on the map.
        lat:       List of latitude coordinates of the locations.
        lon:       List of longitude coordinates of the locations.

    Returns:
        Figure: Map with the points specified in the inputs
    """

    # Creating a map with the provided markers using their latitude and longitude coordinates.
    fig = go.Figure(
        go.Scattermapbox(lat=lat, lon=lon, mode='markers', marker=go.scattermapbox.Marker(size=11), hovertext=text_list)
    )

    # Update the map by centering it on of the the provided longitude and latitude coordinates
    fig.update_layout(
        mapbox_style='open-street-map',
        hovermode='closest',
        mapbox=dict(bearing=0, center=go.layout.mapbox.Center(lat=lat[1], lon=lon[1]), pitch=0, zoom=10),
    )
    return fig


def run(
    origin: str,
    destination: str,
    arrival_date: str,
    age: int,
    trip_duration: int,
    interests: List[str],
    cuisine_preferences: List[str],
    children: bool,
    budget: int,
    model_name:str='Meta-Llama-3.1-70B-Instruct'
) -> Tuple[str, go.Figure]:
    """
    Run the specfied query using Crew AI agents.

    Args:
        origin: Origin city of the traveller.
        destination: Destination to which the traveller is going.
        arrival_date: Approximate date when the trip will begin in epoch time.
        age: Age profile of traveller.
        interests: Specific interests of the traveller.
        cuisine_preferences: Specific cuisine preferences of the traveller.
        children: Whether traveller has children travelling with them.
        budget: Total budget of traveller in US Dollars.

    Returns:
        Returns a tuple containing the itinerary and map
    """
    # Gradio Datetime is currently not working on HF
    # See https://github.com/gradio-app/gradio/issues/10358
    # Hece disabling datetime input and reverting back to string input
    """
    if arrival_date:
        arrival_date_input = datetime.datetime.fromtimestamp(arrival_date).strftime("%m-%d-%Y")
    else:
        arrival_date_input = None
    """
    if arrival_date:
        arrival_date_input = arrival_date.strip()
    else:
        arrival_date_input = None

    log_query(origin, destination, age, trip_duration, budget)
    logger.info(
        f'Origin: {origin}, Destination: {destination}, Arrival Date: {arrival_date_input},'
        f' Age: {age}, Duration: {trip_duration},'
        f' Interests: {interests}, Cuisines: {cuisine_preferences},'
        f' Children: {children}, Daily Budget: {budget}, Model Name: {model_name}'
    )

    # Creating a dictionary of user provided preferences and providing these to the crew agents
    # to work on.

    user_preferences = {
        'origin': origin,
        'destination': destination,
        'arrival_date': arrival_date_input,
        'age': age,
        'trip_duration': trip_duration,
        'interests': interests,
        'cuisine_preferences': cuisine_preferences,
        'children': children,
        'budget': budget,
    }
    #result = TravelCrew(model_name).crew().kickoff(inputs=user_preferences)
    crew = TravelCrew(model_name).crew()
    result = crew.kickoff(inputs=user_preferences)
    metrics = crew.usage_metrics
    logger.info("Result Metrics")
    logger.info(metrics)

    """
        Now we will pass the result to a address summary crew whose job is to extract position
        coordinates of the addresses (latitude and longitude), so that the addresses in the
        result can be displayed in map coordinates
    """

    inputs_for_address = {'text': str(result)}

    addresses = AddressSummaryCrew(model_name).crew().kickoff(inputs=inputs_for_address)

    """
        We have requested the crew agent to return latitude, longitude coordinates.
        But the exact way the LLMs return varies. Hence we try multiple different ways of
        extracting addresses in JSON format from the result.
    """
    json_addresses = None
    if addresses.json_dict is not None:
        json_addresses = addresses.json_dict
    if json_addresses is None:
        try:
            json_addresses = json.loads(addresses.raw)
        except json.JSONDecodeError as e:
            # Try with different format of result data generated with ```json and ending with ```.
            try:
                json_addresses = json.loads(addresses.raw[8:-4])
            except json.JSONDecodeError as e:
                # Try with different format of result data generated with ``` and ending with ```.
                try:
                    json_addresses = json.loads(addresses.raw[4:-4])
                except json.JSONDecodeError as e:
                    logger.error('Error loading Crew Output for addresses')
                    logger.info(addresses.raw)
                    return (result, None)
    fig = filter_map(json_addresses['name'], json_addresses['lat'], json_addresses['lon'])
    return (result, fig)


logger = logging.getLogger()
logger.setLevel(logging.INFO)

with gr.Blocks() as demo:
    gr.Markdown('Use this app to create a detailed itinerary on how to explore a new place.'
                ' Itinerary is customized to your taste. Powered by Sambanova Cloud.')
    # Store context between interactions
    context = gr.State()
    with gr.Row():
        with gr.Column(scale=1):
            inp_source = gr.Textbox(label='Where are you travelling from?')
            inp_dest = gr.Textbox(label='Where are you going?')
            inp_cal = gr.Textbox(label='Approximate arrival date in mm-dd-yyyy')
            inp_age = gr.Slider(label='Your age?', value=30, minimum=15, maximum=90, step=5)
            inp_days = gr.Slider(label='How many days are you travelling?', value=5, minimum=1, maximum=14, step=1)
            inp_interests =\
            gr.CheckboxGroup(
                [
                   'Museums',
                   'Outdoor Adventures',
                   'Shopping',
                   'Children\'s Entertainment',
                   'Off the beat activities',
                   'Night Life',
                ],
               label='Checkbox your interests.',
            )
            inp_cuisine =\
            gr.CheckboxGroup(
                [
                    'Ethnic',
                    'American',
                    'Italian',
                    'Mexican',
                    'Chinese',
                    'Japanese',
                    'Indian',
                    'Thai',
                    'French',
                    'Vietnamese',
                    'Vegan',
               ],
               label='Checkbox your cuisine preferences.',
            )
            inp_children = gr.Checkbox(label='Check if children are travelling with you')
            inp_budget =\
               gr.Slider(
               label='Total budget of trip in USD', show_label=True, value=1000, minimum=500, maximum=10000, step=500
            )
            inp_model = gr.Dropdown(["Meta-Llama-3.3-70B-Instruct",
                                     "DeepSeek-V3-0324",
                                     "Llama-4-Maverick-17B-128E-Instruct",
                                     "Meta-Llama-3.1-8B-Instruct"],
                                    label='Sambanova Model Name',
                                    info='We add models as Sambanova supports them')
            plan_button = gr.Button("Plan your Trip")
        inputs = [inp_source, inp_dest, inp_cal, inp_age, inp_days, inp_interests, inp_cuisine, inp_children, inp_budget, inp_model]

        with gr.Column(scale=2):
            with gr.Row():
                output_itinerary =\
                gr.Textbox(
                    label='Complete Personalized Itinerary of your Trip',
                    show_label=True,
                    show_copy_button=True,
                    autoscroll=False,
                )

            # Chat interface (hidden initially)
            with gr.Row(visible=False) as chat_interface:
                chatbot = gr.Chatbot(label='Chat with the itinerary')
                input_msg = gr.Textbox(label='Ask a question')

            # Chat controls
            start_chat_btn = gr.Button("Start Chat", visible=False)

            # Download button
            download_btn = gr.Button("Download Itinerary")

            output_map = gr.Plot(label='Venues on a Map. Please verify with a Navigation System before traveling.')
            output = [output_itinerary, output_map]

    plan_button.click(fn=run, inputs=inputs, outputs=output).then(
                          lambda: gr.Button(visible=True),
                          outputs=start_chat_btn)

    download_btn_hidden = gr.DownloadButton(visible=False, elem_id="download_btn_hidden")
    download_btn.click(fn=export_pdf, inputs=[output_itinerary, chatbot], outputs=[download_btn_hidden]).then(fn=None, inputs=None, outputs=None, js="() => document.querySelector('#download_btn_hidden').click()")

    start_chat_btn.click(
        start_chat,
        inputs=output_itinerary,
        outputs=[chatbot, input_msg, context]
    ).then(
        lambda: gr.Row(visible=True),
        outputs=chat_interface
    ).then(
        lambda: gr.Button(visible=False),
        outputs=start_chat_btn)

    input_msg.submit(
        respond,
        inputs=[input_msg, chatbot, context, inp_model],
        outputs=[input_msg, chatbot]
    )

demo.launch()

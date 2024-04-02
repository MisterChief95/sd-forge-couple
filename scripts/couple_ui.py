from modules.ui_components import FormRow, ToolButton
from PIL import Image, ImageDraw
import gradio as gr


headers = ["x", "y", "weight"]
data_value = [["0:0.5", "0.0:1.0", "1.0"], ["0.5:1.0", "0.0:1.0", "1.0"]]


def parse_mapping(data: list) -> list:
    mapping = []

    for [X, Y, W] in data:
        if not X.strip():
            continue

        mapping.append(
            (
                (float(X.split(":")[0]), float(X.split(":")[1])),
                (float(Y.split(":")[0]), float(Y.split(":")[1])),
                float(W),
            )
        )

    return mapping


def validata_mapping(data: list) -> bool:
    try:
        for [X, Y, W] in data:
            if not X.strip():
                continue

            float(X.split(":")[0])
            float(X.split(":")[1])
            float(Y.split(":")[0])
            float(Y.split(":")[1])
            float(W)

        return True

    except AssertionError:
        print("\n\n[Couple] Incorrect number of : in Mapping...\n\n")
        return False
    except ValueError:
        print("\n\n[Couple] Non-Number in Mapping...\n\n")
        return False


def visualize_mapping(p_WIDTH: int, p_HEIGHT: int, data: list) -> Image:
    if not (validata_mapping(data)):
        return None

    COLORS = ("red", "orange", "yellow", "green", "blue", "violet", "purple", "white")

    matt = Image.new("RGB", (p_WIDTH, p_HEIGHT), "black")
    draw = ImageDraw.Draw(matt)

    mapping = parse_mapping(data)

    print("\nAdv. Preview:")
    for tile_index in range(len(mapping)):
        color_index = tile_index % len(COLORS)

        (X, Y, W) = mapping[tile_index]
        x_from = int(p_WIDTH * X[0])
        x_to = int(p_WIDTH * X[1])
        y_from = int(p_HEIGHT * Y[0])
        y_to = int(p_HEIGHT * Y[1])
        weight = W

        print(f"  [{y_from:4d}:{y_to:4d}, {x_from:4d}:{x_to:4d}] = {weight:.2f}")
        draw.rectangle(
            [(x_from, y_from), (x_to, y_to)], outline=COLORS[color_index], width=2
        )

    return matt


def clear_dataframe():
    return {"headers": headers, "data":data_value}


def add_global_row_fn(df: list) -> list:
    return [["0:1", "0:1", "1"]] + df
    

def delete_first_row_fn(df: list) -> list:
    return df[1:] if len(df) > 2 else df


def delete_last_row_fn(df: list) -> list:
    return df[:-1] if len(df) > 2 else df

def delete_by_row_num_fn(df: list, row_num: int) -> list:
    row = max(0, min(int(row_num)-1, len(df)-1))
    df.pop(row)
    return df


def couple_UI(script, title: str):
    with gr.Accordion(label=title, open=False):
        with gr.Row():
            enable = gr.Checkbox(label="Enable", elem_id="fc_enable")

        with gr.Row():
            mode = gr.Radio(
                ["Basic", "Advanced"],
                label="Region Assignment",
                value="Basic",
            )

            separator = gr.Textbox(
                label="Couple Separator",
                lines=1,
                max_lines=1,
                placeholder="Leave empty to use newline",
            )

        with gr.Group() as basic_settings:
            with gr.Row():
                direction = gr.Radio(
                    ["Horizontal", "Vertical"],
                    label="Tile Direction",
                    value="Horizontal",
                    scale=1
                )

                background = gr.Radio(
                    ["None", "First Line", "Last Line"],
                    label="Global Effect",
                    value="None",
                    scale=3
                )

        with gr.Group(visible=False, elem_id="fc_adv") as adv_settings:
            with gr.Column():
                with FormRow():
                    add_global_row = gr.Button("Add Global Row", variant="secondary", scale=2, elem_classes="fc_button_left fc_button")
                    delete_first_row = gr.Button("Delete First Row", variant="secondary", scale=2, elem_classes="fc_button")
                    delete_last_row = gr.Button("Delete Last Row", variant="secondary", scale=2, elem_classes="fc_button")
                    delete_by_row_num = gr.Button("Delete Row #", variant="secondary", elem_classes="fc_button")
                    row_num = gr.Number(minimum=1, maximum=100, step=1, value=1, variant="secondary", elem_classes="dimensions-tools", elem_id="fc_delete_num_input", show_label=False)

                mapping = gr.Dataframe(
                    elem_id="fc_mapping",
                    label="Mapping",
                    headers=headers,
                    datatype="str",
                    row_count=(2, "dynamic"),
                    col_count=(3, "fixed"),
                    interactive=True,
                    type="array",
                    value=data_value,
                )

                with FormRow():
                    with gr.Column(scale=4):
                        preview_width = gr.Slider(minimum=64, maximum=4096, step=64, label="Width", value=1024, elem_id="couple_width")
                        preview_height = gr.Slider(minimum=64, maximum=4096, step=64, label="Height", value=1024, elem_id="couple_height")

                    with gr.Column(scale=1):
                        res_switch_btn = ToolButton(value='\U000021C5', elem_id="couple_res_switch_btn", tooltip="Switch width/height")
                    
                    res_switch_btn.click(fn=None, _js="function(){switchCoupleWidthHeight()}", inputs=None, outputs=None, show_progress=False)

                with gr.Row():
                    preview_btn = gr.Button("Preview Mapping", elem_classes="fc_button")

                    reset_table = gr.Button("Reset Mapping", elem_classes="fc_button")
                    reset_table.click(clear_dataframe, None, mapping)

                preview_img = gr.Image(
                    image_mode="RGB",
                    label="Mapping Preview",
                    type="pil",
                    interactive=False,
                    height=512,
                )

                preview_btn.click(
                        visualize_mapping,
                        [preview_width, preview_height, mapping],
                        preview_img,
                    )

                add_global_row.click(add_global_row_fn, mapping, mapping)
                delete_first_row.click(delete_first_row_fn, mapping, mapping)
                delete_last_row.click(delete_last_row_fn, mapping, mapping)
                delete_by_row_num.click(delete_by_row_num_fn, [mapping, row_num], mapping)


        def on_radio_change(choice):
            if choice == "Basic":
                return [
                    gr.Group.update(visible=True),
                    gr.Group.update(visible=False),
                ]
            else:
                return [
                    gr.Group.update(visible=False),
                    gr.Group.update(visible=True),
                ]

        mode.change(on_radio_change, mode, [basic_settings, adv_settings])

        script.paste_field_names = []
        script.infotext_fields = [
            (enable, "forge_couple"),
            (direction, "forge_couple_direction"),
            (background, "forge_couple_background"),
            (separator, "forge_couple_separator"),
            (mode, "forge_couple_mode"),
            (mapping, "forge_couple_mapping"),
        ]

        for comp, name in script.infotext_fields:
            comp.do_not_save_to_config = True
            script.paste_field_names.append(name)

        return [enable, direction, background, separator, mode, mapping]

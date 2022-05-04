last_print_length = 0

def show_on_screen(str):
    print(str, end="\r")
    global last_print_length
    last_print_length = len(str)

def clean_screen():
    global last_print_length
    print(' ' * last_print_length, end="\r")

def output_to_file(output, file_path):
    file = open(file_path, "w+")
    file.write(output)
    file.close()

def output_to_screen(output):
    clean_screen()
    print(output)
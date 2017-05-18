import tkinter as tk

from helper import BG_COLOR, f_tracking, f_answers


class TestSession:
    """Represents a test session for the assessment of images."""

    def __init__(self, images, question, possible_answers, answers_description, show_preview, preload_images, test_image_side):
        """Initializes a test session.
        
        :param images: The light-field images to use for the test session.
        :param question: The question that should be asked.
        :param possible_answers: The possible answers to the question.
        :param answers_description: A short text describing the possible answers to the question.
        """
        self.images = images
        self.question = question
        self.possible_answers = possible_answers
        self.answers_description = answers_description
        self.show_preview = show_preview
        self.panels = None
        self.img_index = 0
        self.img_index_label = None
        self.message_label = None
        self.cur_img = images[self.img_index]
        self.answers = [None] * len(images)

        self.root = tk.Tk()
        self.root.title("lf-tracking")
        self.root.configure(background=BG_COLOR)
        self.root.geometry("{0}x{1}+0+0".format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))

        self.setup_gui()

        # Link the panels to each image
        for img in self.images:
            img.set_panels(self.panels)
            if(preload_images):
                img.load_images()

            img.set_test_image_side(test_image_side)

        self.display_img_index()

        # Start by either showing the preview or the normal interactive view
        if (self.show_preview):
            self.cur_img.preview()
        else:
            self.cur_img.update_images()

        self.root.mainloop()

    def setup_gui(self):
        """Sets up the graphical user interface needed for the test session"""

        # Main frame containing all GUI objects
        main_frame = tk.Frame(background=BG_COLOR)

        self.img_index_label = tk.Label(main_frame, background=BG_COLOR, pady=10)
        self.img_index_label.grid(row=0, column=0, columnspan=3)

        tk.Label(main_frame, text="Test", background=BG_COLOR).grid(row=1, column=0, pady=5)
        tk.Label(main_frame, text="Reference", background=BG_COLOR).grid(row=1, column=2)

        # Panels where the two images are displayed
        self.panels = [tk.Label(main_frame, background=BG_COLOR), tk.Label(main_frame, background=BG_COLOR)]
        self.panels[0].grid(row=2, column=0)
        self.panels[1].grid(row=2, column=2)

        self.panels[0].bind('<Button-1>', self.click)
        self.panels[0].bind('<B1-Motion>', self.move)
        self.panels[0].bind('<Double-Button-1>', self.refocus_to_point)
        self.panels[1].bind('<Button-1>', self.click)
        self.panels[1].bind('<B1-Motion>', self.move)
        self.panels[1].bind('<Double-Button-1>', self.refocus_to_point)

        question_label = tk.Label(main_frame, text=self.question, background=BG_COLOR, pady=30)
        question_label.grid(row=3, column=0, columnspan=3)

        # Frame containing all the buttons representing the possible answers
        buttons_frame = tk.Frame(main_frame, background=BG_COLOR)

        for i in range(len(self.possible_answers)):
            answer = self.possible_answers[i]
            btn_width = 12
            btn = tk.Button(buttons_frame, text=str(answer), command=lambda a=answer: self.answer(a),
                            width=btn_width, highlightbackground=BG_COLOR)
            btn.grid(row=0, column=i, padx=12)
            tk.Label(buttons_frame, text=self.answers_description[i], width=btn_width, wraplength=btn_width*10, background=BG_COLOR).grid(row=1, column=(i))

            # We can answer with the keys 1-9 if the number of answers is smaller than 10
            if len(self.possible_answers) <= 9:
                self.root.bind(str(i + 1), lambda e, a=self.possible_answers[i]: self.answer(a))

        buttons_frame.grid(row=5, column=0, columnspan=3)

        main_frame.place(anchor="c", relx=.50, rely=.50)

    def next_img(self, event):
        """Displays the next image"""

        if not self.is_last_image():
            self.cur_img.close_img()
            self.cur_img.cur_time = 0
            self.img_index += 1
            self.cur_img = self.images[self.img_index]

            self.display_img_index()
            f_tracking.write("\n")

            if(self.show_preview):
                self.cur_img.preview()
            else:
                self.cur_img.update_images()

    def answer(self, answ):
        """Stores the answer given by the user.
        
        :param answ: The answer.
        """
        self.answers[self.img_index] = answ
        f_answers.write("{:30} : {}\n".format(self.cur_img.img_name, answ))

        if self.is_last_image():
            self.finish_test_session()
        else:
            self.next_img(None)

    def click(self, event):
        """Method  called whenever an image is clicked on."""

        self.cur_img.click((event.x, event.y))
        return

    def move(self, event):
        """Method  called when the mouse is dragged over an image."""

        self.cur_img.move((event.x, event.y))
        return

    def refocus_to_depth(self, focus_depth):
        """Displays the image corresponding to the given focus depth.
        
        :param focus_depth: The depth to focus to image on.
        """
        self.cur_img.refocus_to_depth(focus_depth)

    def refocus_to_point(self, event):
        """Refocus the current image on the given point using the depth map

        :param event: The event that triggered the refocusing and contains the point coordinates
        """
        self.cur_img.refocus_to_point(event)

    def display_img_index(self):
        """Displays the index of the current image in a text label."""

        self.img_index_label.configure(text="Image {}/{}".format(self.img_index + 1, len(self.images)))

    def is_last_image(self):
        """Return True iff the current image displayed is the last one."""

        return self.img_index >= (len(self.images) - 1)

    def finish_test_session(self):
        self.cur_img.close_img()

        f_tracking.flush()
        f_tracking.close()
        f_answers.flush()
        f_answers.close()

        end_msg = tk.Label(self.root, text="FINISHED", background=BG_COLOR)
        end_msg.pack(fill="both", expand="true")

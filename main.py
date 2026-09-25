import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from comicvine.client import ComicVineClient
from comicvine.service import ComicVineService
from pipeline.batch import BatchPipeline
from models.comic import Comic
from models.overrides import MetadataOverrides


class ComicManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("ComicManager")
        self.geometry("900x700")
        self.minsize(800, 600)

        self.selected_files: list[Path] = []
        self.override_entries = {}

        self.comicvine = ComicVineService(
            ComicVineClient()
        )

        self.batch_pipeline = BatchPipeline(
            self.comicvine
        )

        self.show_home()

    # =========================================================
    # General UI
    # =========================================================

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def create_title(self, title: str, description: str | None = None):
        ttk.Label(
            self,
            text=title,
            font=("TkDefaultFont", 18, "bold")
        ).pack(pady=(20, 5))

        if description:
            ttk.Label(
                self,
                text=description,
                wraplength=750
            ).pack(pady=(0, 20))

    def back_button(self, command):
        ttk.Button(
            self,
            text="Back",
            command=command
        ).pack(side="bottom", pady=15)

    # =========================================================
    # Home
    # =========================================================

    def show_home(self):
        self.clear_window()

        self.create_title(
            "ComicManager",
            "Manage comic metadata and CBZ files."
        )

        ttk.Button(
            self,
            text="ComicVine Metadata",
            command=self.show_file_selection
        ).pack(
            ipadx=40,
            ipady=12,
            pady=10
        )

        ttk.Button(
            self,
            text="Exit",
            command=self.destroy
        ).pack(pady=20)

    # =========================================================
    # File selection
    # =========================================================

    def show_file_selection(self):
        self.clear_window()

        self.create_title(
            "Select Comic Files",
            "Select the CBZ files you want to process."
        )

        ttk.Button(
            self,
            text="Select CBZ Files",
            command=self.select_files
        ).pack(pady=10)

        self.file_list = tk.Listbox(
            self,
            width=90,
            height=18
        )

        self.file_list.pack(
            padx=30,
            pady=10,
            fill="both",
            expand=True
        )

        self.file_count_label = ttk.Label(
            self,
            text="No files selected."
        )

        self.file_count_label.pack(pady=5)

        controls = ttk.Frame(self)
        controls.pack(pady=10)

        ttk.Button(
            controls,
            text="Clear",
            command=self.clear_files
        ).pack(side="left", padx=5)

        ttk.Button(
            controls,
            text="Continue",
            command=self.show_overrides
        ).pack(side="left", padx=5)

        self.back_button(self.show_home)

    def select_files(self):
        filenames = filedialog.askopenfilenames(
            title="Select CBZ files",
            filetypes=[
                ("Comic Book Archives", "*.cbz"),
                ("All files", "*.*")
            ]
        )

        if not filenames:
            return

        self.selected_files = [
            Path(filename)
            for filename in filenames
        ]

        self.refresh_file_list()

    def refresh_file_list(self):
        self.file_list.delete(0, tk.END)

        for path in self.selected_files:
            self.file_list.insert(
                tk.END,
                path.name
            )

        self.file_count_label.config(
            text=f"{len(self.selected_files)} file(s) selected."
        )

    def clear_files(self):
        self.selected_files = []
        self.refresh_file_list()

    # =========================================================
    # Metadata overrides
    # =========================================================

    def show_overrides(self):
        if not self.selected_files:
            messagebox.showwarning(
                "No files selected",
                "Please select at least one CBZ file."
            )
            return

        self.clear_window()

        self.create_title(
            "Metadata Overrides",
            (
                "Any field you enter here will override the "
                "ComicVine value for every file in this batch. "
                "Leave fields blank to keep the ComicVine value."
            )
        )

        container = ttk.Frame(self)
        container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=10
        )

        canvas = tk.Canvas(container)

        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=canvas.yview
        )

        fields_frame = ttk.Frame(canvas)

        fields_frame.bind(
            "<Configure>",
            lambda event: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window(
            (0, 0),
            window=fields_frame,
            anchor="nw"
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.override_entries = {}

        fields = [
            ("Series", "series", "text"),
            ("Issue", "issue", "text"),
            ("Title", "title", "text"),
            ("Volume", "volume", "int"),
            ("Count", "count", "int"),
            ("Alternate Series", "alternate_series", "text"),
            ("Alternate Number", "alternate_number", "text"),
            ("Alternate Count", "alternate_count", "int"),
            ("Genre", "genre", "text"),
            ("Story Arc", "story_arc", "text"),
            ("Story Arc Number", "story_arc_number", "text"),
            ("Series Group", "series_group", "text"),

            ("Synopsis", "synopsis", "text"),
            ("Characters", "characters", "list"),
            ("Teams", "teams", "list"),
            ("Locations", "locations", "list"),
            ("Main Character / Team", "main_character_or_team", "text"),

            ("Writers", "writers", "list"),
            ("Pencillers", "pencillers", "list"),
            ("Inkers", "inkers", "list"),
            ("Colorists", "colorists", "list"),
            ("Letterers", "letterers", "list"),
            ("Cover Artists", "cover_artists", "list"),
            ("Editors", "editors", "list"),
            ("Translators", "translators", "list"),
            ("Imprint", "imprint", "text"),

            ("Day", "day", "int"),
            ("Month", "month", "int"),
            ("Year", "year", "int"),
            ("Publisher", "publisher", "text"),
            ("Format", "format", "text"),
            ("Language ISO", "language_iso", "text"),
            ("Web", "web", "text"),
            ("Page Count", "page_count", "int"),
            ("Black and White", "black_and_white", "bool"),
            ("Manga", "manga", "text"),
            ("Scan Information", "scan_information", "text"),
            ("Age Rating", "age_rating", "text"),
            ("Community Rating", "community_rating", "float"),
            ("GTIN", "gtin", "text"),

            ("Review", "review", "text"),
            ("Notes", "notes", "text"),
            ("Tags", "tags", "list"),
        ]

        for row, (label, field, field_type) in enumerate(fields):
            ttk.Label(
                fields_frame,
                text=label
            ).grid(
                row=row,
                column=0,
                sticky="w",
                padx=10,
                pady=5
            )

            if field_type == "bool":
                variable = tk.StringVar(value="")

                widget = ttk.Combobox(
                    fields_frame,
                    textvariable=variable,
                    values=["", "Yes", "No"],
                    state="readonly",
                    width=47
                )

                self.override_entries[field] = (
                    widget,
                    field_type
                )

            else:
                widget = ttk.Entry(
                    fields_frame,
                    width=50
                )

                self.override_entries[field] = (
                    widget,
                    field_type
                )

            widget.grid(
                row=row,
                column=1,
                sticky="ew",
                padx=10,
                pady=5
            )

        fields_frame.columnconfigure(
            1,
            weight=1
        )

        controls = ttk.Frame(self)
        controls.pack(pady=10)

        ttk.Button(
            controls,
            text="Back",
            command=self.show_file_selection
        ).pack(
            side="left",
            padx=5
        )

        ttk.Button(
            controls,
            text="Search ComicVine",
            command=self.search_comicvine
        ).pack(
            side="left",
            padx=5
        )

    def get_overrides(self) -> MetadataOverrides:
        values = {}

        for field, (widget, field_type) in self.override_entries.items():
            value = widget.get().strip()

            if value == "":
                continue

            if field_type == "int":
                try:
                    value = int(value)
                except ValueError:
                    raise ValueError(
                        f"{field} must be an integer."
                    )

            elif field_type == "float":
                try:
                    value = float(value)
                except ValueError:
                    raise ValueError(
                        f"{field} must be a number."
                    )

            elif field_type == "list":
                value = [
                    item.strip()
                    for item in value.split(",")
                    if item.strip()
                ]

            elif field_type == "bool":
                value = value == "Yes"

            values[field] = value

        return MetadataOverrides(**values)

    # =========================================================
    # ComicVine identification
    # =========================================================

    def search_comicvine(self):
        try:
            self.overrides = self.get_overrides()

        except Exception as error:
            messagebox.showerror(
                "Invalid Override",
                str(error)
            )
            return

        try:
            self.identification = (
                self.batch_pipeline.identify(
                    self.selected_files
                )
            )

        except Exception as error:
            messagebox.showerror(
                "ComicVine Search Failed",
                str(error)
            )
            return

        self.show_volume_selection()

    # =========================================================
    # Volume selection
    # =========================================================

    def show_volume_selection(self):
        self.clear_window()

        self.create_title(
            "Select ComicVine Volume",
            (
                f"Series: {self.identification.series}\n"
                f"{len(self.identification.items)} file(s)"
            )
        )

        columns = (
            "name",
            "year",
            "publisher",
            "issues"
        )

        self.volume_tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            height=15
        )

        self.volume_tree.heading(
            "name",
            text="Volume"
        )

        self.volume_tree.heading(
            "year",
            text="Year"
        )

        self.volume_tree.heading(
            "publisher",
            text="Publisher"
        )

        self.volume_tree.heading(
            "issues",
            text="Issues"
        )

        self.volume_tree.column(
            "name",
            width=350
        )

        self.volume_tree.column(
            "year",
            width=80
        )

        self.volume_tree.column(
            "publisher",
            width=180
        )

        self.volume_tree.column(
            "issues",
            width=80
        )

        self.volume_tree.pack(
            padx=25,
            pady=10,
            fill="both",
            expand=True
        )

        for candidate in self.identification.candidates:
            volume = candidate.volume

            publisher = volume.get("publisher")

            if isinstance(publisher, dict):
                publisher = publisher.get("name")

            self.volume_tree.insert(
                "",
                tk.END,
                iid=str(volume["id"]),
                values=(
                    volume.get("name", ""),
                    volume.get("start_year", ""),
                    publisher or "",
                    volume.get("count_of_issues", "")
                )
            )

        ttk.Button(
            self,
            text="Use Selected Volume",
            command=self.select_volume
        ).pack(pady=10)

        self.back_button(self.show_overrides)

    def select_volume(self):
        selection = self.volume_tree.selection()

        if not selection:
            messagebox.showwarning(
                "No Volume Selected",
                "Please select a ComicVine volume."
            )
            return

        volume_id = int(selection[0])

        try:
            self.batch_pipeline.select_volume(
                self.identification,
                volume_id
            )

            self.issue_results = (
                self.batch_pipeline.resolve_issues(
                    self.identification
                )
            )

        except Exception as error:
            messagebox.showerror(
                "Issue Resolution Failed",
                str(error)
            )
            return

        self.show_review()

    # =========================================================
    # Review
    # =========================================================

    def show_review(self):
        self.clear_window()

        self.create_title(
            "Review",
            (
                f"{self.identification.series} — "
                f"{len(self.issue_results)} issue(s)"
            )
        )

        columns = (
            "file",
            "issue",
            "status"
        )

        tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            height=18
        )

        tree.heading(
            "file",
            text="File"
        )

        tree.heading(
            "issue",
            text="Issue"
        )

        tree.heading(
            "status",
            text="Status"
        )

        tree.column(
            "file",
            width=450
        )

        tree.column(
            "issue",
            width=100
        )

        tree.column(
            "status",
            width=150
        )

        tree.pack(
            padx=25,
            pady=10,
            fill="both",
            expand=True
        )

        for result in self.issue_results:
            status = (
                "Resolved"
                if result.comic is not None
                else "Unresolved"
            )

            tree.insert(
                "",
                tk.END,
                values=(
                    result.source.name,
                    result.parsed.issue,
                    status
                )
            )

        unresolved = [
            result
            for result in self.issue_results
            if result.comic is None
        ]

        if unresolved:
            ttk.Label(
                self,
                text=(
                    f"{len(unresolved)} issue(s) could not be "
                    "resolved and will be skipped."
                )
            ).pack(pady=5)

        ttk.Button(
            self,
            text="Process Files",
            command=self.process_batch
        ).pack(pady=10)

        self.back_button(self.show_volume_selection)

    # =========================================================
    # Processing
    # =========================================================

    def process_batch(self):
        try:
            results = self.batch_pipeline.process(
                self.issue_results,
                overrides=self.overrides
            )

        except Exception as error:
            messagebox.showerror(
                "Processing Failed",
                str(error)
            )
            return

        successful = sum(
            result.success
            for result in results
        )

        unresolved = sum(
            result.status.value == "unresolved"
            for result in results
        )

        failed = sum(
            result.status.value == "failed"
            for result in results
        )

        messagebox.showinfo(
            "Processing Complete",
            (
                f"Processing complete.\n\n"
                f"Successful: {successful}\n"
                f"Unresolved: {unresolved}\n"
                f"Failed: {failed}"
            )
        )

        self.show_home()


if __name__ == "__main__":
    app = ComicManagerApp()
    app.mainloop()
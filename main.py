import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os


class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Watermark Tool")
        self.root.geometry("900x700")
        self.root.configure(bg="#2b2b2b")

        self.original_image = None
        self.preview_image = None
        self.image_path = None

        self._build_ui()

    def _build_ui(self):
        # Top toolbar
        toolbar = tk.Frame(self.root, bg="#1e1e1e", pady=8)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        tk.Button(toolbar, text="📂 Open Image", command=self.open_image,
                  bg="#3a7bd5", fg="white", padx=12, pady=5,
                  relief=tk.FLAT).pack(side=tk.LEFT, padx=8)

        tk.Button(toolbar, text="💾 Save As", command=self.save_image,
                  bg="#27ae60", fg="white", padx=12, pady=5,
                  relief=tk.FLAT).pack(side=tk.LEFT, padx=8)

        # FIXED: Reset button now actually resets the text, sliders, and colors
        tk.Button(toolbar, text="🔄 Reset Settings", command=self.reset_settings,
                  bg="#8e44ad", fg="white", padx=12, pady=5,
                  relief=tk.FLAT).pack(side=tk.LEFT, padx=8)

        # Main layout: canvas + controls
        main = tk.Frame(self.root, bg="#2b2b2b")
        main.pack(fill=tk.BOTH, expand=True)

        # Preview canvas
        self.canvas = tk.Canvas(main, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Controls panel
        controls = tk.Frame(main, bg="#2b2b2b", width=280)
        controls.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        controls.pack_propagate(False)

        # Watermark text
        tk.Label(controls, text="Watermark Text:", bg="#2b2b2b",
                 fg="white", anchor="w").pack(fill=tk.X, pady=(5, 2))
        self.text_entry = tk.Entry(controls, font=("Arial", 11))
        self.text_entry.insert(0, "© My Watermark")
        self.text_entry.pack(fill=tk.X, pady=4)
        self.text_entry.bind("<KeyRelease>", lambda e: self.refresh_preview())

        # Font size
        tk.Label(controls, text="Font Size:", bg="#2b2b2b",
                 fg="white", anchor="w").pack(fill=tk.X, pady=(10, 2))
        self.size_var = tk.IntVar(value=48)
        self.size_scale = tk.Scale(controls, from_=10, to=300,
                                   orient=tk.HORIZONTAL, variable=self.size_var,
                                   bg="#2b2b2b", fg="white", highlightthickness=0,
                                   command=lambda e: self.refresh_preview())
        self.size_scale.pack(fill=tk.X)

        # Opacity
        tk.Label(controls, text="Opacity:", bg="#2b2b2b",
                 fg="white", anchor="w").pack(fill=tk.X, pady=(10, 2))
        self.opacity_var = tk.IntVar(value=120)
        self.opacity_scale = tk.Scale(controls, from_=0, to=255, orient=tk.HORIZONTAL,
                                      variable=self.opacity_var, bg="#2b2b2b", fg="white",
                                      highlightthickness=0,
                                      command=lambda e: self.refresh_preview())
        self.opacity_scale.pack(fill=tk.X)

        # Color
        tk.Label(controls, text="Color:", bg="#2b2b2b",
                 fg="white", anchor="w").pack(fill=tk.X, pady=(10, 2))
        self.color_var = tk.StringVar(value="white")
        color_row = tk.Frame(controls, bg="#2b2b2b")
        color_row.pack(fill=tk.X, pady=4)
        for c in ["white", "black", "red", "yellow", "cyan", "orange"]:
            tk.Button(color_row, bg=c, width=3, height=1, relief=tk.FLAT,
                      command=lambda col=c: self._set_color(col)
                      ).pack(side=tk.LEFT, padx=2)

        # Position
        tk.Label(controls, text="Position:", bg="#2b2b2b",
                 fg="white", anchor="w").pack(fill=tk.X, pady=(10, 2))
        self.position_var = tk.StringVar(value="bottom-right")
        self.pos_combobox = ttk.Combobox(controls, textvariable=self.position_var,
                                         values=["top-left", "top-right", "bottom-left",
                                                 "bottom-right", "center", "tile"],
                                         state="readonly")
        self.pos_combobox.pack(fill=tk.X, pady=4)
        self.pos_combobox.bind("<<ComboboxSelected>>", lambda e: self.refresh_preview())

        # Rotation
        tk.Label(controls, text="Rotation (°):", bg="#2b2b2b",
                 fg="white", anchor="w").pack(fill=tk.X, pady=(10, 2))
        self.rotation_var = tk.IntVar(value=0)
        self.rotation_scale = tk.Scale(controls, from_=-90, to=90, orient=tk.HORIZONTAL,
                                       variable=self.rotation_var, bg="#2b2b2b", fg="white",
                                       highlightthickness=0,
                                       command=lambda e: self.refresh_preview())
        self.rotation_scale.pack(fill=tk.X)

    def _set_color(self, color):
        self.color_var.set(color)
        self.refresh_preview()

    # ---------- NEW: Reset Function ----------
    def reset_settings(self):
        self.text_entry.delete(0, tk.END)
        self.text_entry.insert(0, "© My Watermark")
        self.size_var.set(48)
        self.opacity_var.set(120)
        self.color_var.set("white")
        self.position_var.set("bottom-right")
        self.rotation_var.set(0)
        self.refresh_preview()

    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.webp")])
        if not path:
            return
        self.image_path = path
        self.original_image = Image.open(path).convert("RGBA")
        self.refresh_preview()

    def refresh_preview(self):
        if self.original_image is None:
            return
        watermarked = self.apply_watermark(self.original_image.copy())
        self.show_preview(watermarked)

    def apply_watermark(self, img):
        text = self.text_entry.get().strip()
        if not text:
            return img

        wm_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(wm_layer)

        size = self.size_var.get()
        try:
            font = ImageFont.truetype("arial.ttf", size)
        except Exception:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

        color = self.color_var.get()
        opacity = self.opacity_var.get()
        position = self.position_var.get()

        if position == "tile":
            step_x, step_y = tw + 60, th + 60
            for y in range(0, img.height, step_y):
                for x in range(0, img.width, step_x):
                    self._draw_rotated_text(wm_layer, (x, y), text,
                                            font, color, opacity)
        else:
            W, H = img.size
            pad = 20
            coords = {
                "top-left": (pad, pad),
                "top-right": (W - tw - pad, pad),
                "bottom-left": (pad, H - th - pad),
                "bottom-right": (W - tw - pad, H - th - pad),
                "center": ((W - tw) // 2, (H - th) // 2),
            }[position]
            self._draw_rotated_text(wm_layer, coords, text,
                                    font, color, opacity)

        return Image.alpha_composite(img, wm_layer)

    def _draw_rotated_text(self, layer, pos, text, font, color, opacity):
        tmp = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(tmp)
        try:
            rgb = Image.new("RGBA", (1, 1), color).getpixel((0, 0))
        except Exception:
            rgb = (255, 255, 255, 255)
        d.text(pos, text, font=font, fill=(rgb[0], rgb[1], rgb[2], opacity))

        angle = self.rotation_var.get()
        if angle != 0:
            tmp = tmp.rotate(angle, expand=False)

        layer.alpha_composite(tmp)

    def show_preview(self, pil_img):
        self.canvas.update_idletasks()
        cw = max(self.canvas.winfo_width(), 400)
        ch = max(self.canvas.winfo_height(), 400)

        img = pil_img.copy()
        img.thumbnail((cw - 20, ch - 20), Image.LANCZOS)

        self.preview_image = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(cw // 2, ch // 2, image=self.preview_image,
                                 anchor="center")

    # ---------- FIXED: Save Function ----------
    def save_image(self):
        if self.original_image is None:
            messagebox.showwarning("No image", "Please open an image first.")
            return

        # Force the dialog to start with a proper name, without double extensions
        initial_name = "watermarked_image.png"
        if self.image_path:
            base = os.path.splitext(os.path.basename(self.image_path))[0]
            initial_name = f"{base}_watermarked.png"

        out_path = filedialog.asksaveasfilename(
            initialfile=initial_name,
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg;*.jpeg")])

        if not out_path:
            return

        # Prevent the "file not found" / ".png.png" issue
        if not out_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            out_path += '.png'

        try:
            final = self.apply_watermark(self.original_image.copy())

            # If saving as JPEG, remove transparency and convert to RGB
            if out_path.lower().endswith((".jpg", ".jpeg")):
                final = final.convert("RGB")

            final.save(out_path)
            messagebox.showinfo("Saved", f"Successfully saved to:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()
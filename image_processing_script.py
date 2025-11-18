import argparse
from PIL import Image, ImageFilter

def process_image(in_path, out_path, resize=None, grayscale=False, rotate=0, blur=0):
        img = Image.open(in_path)
        
        resample_method = Image.Resampling.LANCZOS

        if resize:
                img = img.(resize,resample_method)

        if grayscale:
                img = img.convert("L")

        if rotate:
                img = img.rotate(rotate, expand=True)

        if blur > 0:
                img = img.filter(ImageFilter.BLUR)

        img.save(out_path,format='png')
        print(f"Saved processed image to: {out_path}")

def parse_args():
        p = argparse.ArgumentParser(description="Very simple Pillow image processor")
        p.add_argument("input", help="Input image path")
        p.add_argument("output", help="Output image path")
        p.add_argument("--resize", nargs=2, type=int, metavar=('W','H'), help="Resize to WIDTH HEIGHT")
        p.add_argument("--grayscale", action="store_true", help="Convert to grayscale")
        p.add_argument("--rotate", type=float, default=0, help="Rotate degrees (clockwise)")
        p.add_argument("--blur", type=float, default=0, help="Gaussian blur radius")
        return p.parse_args()

if __name__ == "__main__":
        args = parse_args()
        resize = tuple(args.resize) if args.resize else None
        process_image(args.input, args.output, resize=resize,
                                    grayscale=args.grayscale, rotate=args.rotate, blur=args.blur)
"""py .\image_processing_script.py .\images\astro.jpg output.png --resize 300 300 --grayscale --blur 2"""        
        
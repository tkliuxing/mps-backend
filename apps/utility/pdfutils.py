import os
import io
import base64
import tempfile
from PIL import Image, ImageOps
from pypdf import PdfWriter, PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def convert_coordinates(page, x, y, scale=1):
    _, _, pdf_w, pdf_h = page.mediabox
    return int(x*scale), int(pdf_h - (y*scale))

def add_image_to_pdf(
        pdf_path, page_number, x, y, max_width, max_height, image_base64, output_path,
        scale=0.6711,
        use_tmp_files=True
):
    # page_number = page_number + 1

    # 打开PDF文件
    pdf = PdfReader(open(pdf_path, 'rb'))

    # 获取指定页的内容
    page = pdf.pages[page_number]

    # 创建临时PDF文件
    if use_tmp_files:
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_pdf_path = temp_file.name
    else:
        temp_pdf_path = output_path+".tmp.pdf"
    _, _, pdf_w, pdf_h = page.mediabox
    temp_pdf = canvas.Canvas(temp_pdf_path, pagesize=(pdf_w, pdf_h,))

    # 将Base64图像解码并绘制到临时PDF文件上
    image_data = base64.b64decode(image_base64)
    img_obj = Image.open(io.BytesIO(image_data))
    img_obj.thumbnail((max_width, max_height))
    width, height = img_obj.size
    white_background = Image.new("RGB", img_obj.size, "white")
    white_background.paste(img_obj, mask=img_obj.split()[3] if img_obj.mode == 'RGBA' else None)
    img_obj = white_background.convert("RGB")
    image = ImageReader(img_obj)
    # 转换坐标系
    x, y = convert_coordinates(page, x, y, scale=scale)
    width=int(width*scale)
    height=int(height*scale)
    y = y - height
    # print('pdf_w, pdf_h', pdf_w, pdf_h)
    # print('x, y, width, height', x, y, width, height)
    temp_pdf.drawImage(image, x, y, mask=[210,255,210,255,210,255])
    # temp_pdf.drawImage(image, x, y, width, height)

    # 保存临时PDF文件
    temp_pdf.showPage()
    temp_pdf.save()

    # 将临时PDF文件合并到输出PDF文件中
    output = PdfWriter()
    temp_pdf = PdfReader(open(temp_pdf_path, 'rb'))
    page.merge_page(temp_pdf.pages[0])

    # 将其他页添加到输出文件中
    for i in range(len(pdf.pages)):
        if i != page_number:
            output.add_page(pdf.pages[i])
        else:
            output.add_page(page)

    # 保存输出文件
    with open(output_path, 'wb') as f:
        output.write(f)

    # 删除临时文件
    if use_tmp_files:
        temp_file.close()
        os.remove(temp_pdf_path)

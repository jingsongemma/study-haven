"""知识文件解析工具。"""

from docx import Document as DocxDocument
from pypdf import PdfReader


class FileLoader:
    """负责从上传文件中抽取文本内容。"""

    @staticmethod
    def load_text(file_path, filename):
        """根据文件扩展名读取 txt、pdf 或 docx 文本。"""
        suffix = filename.rsplit(".", 1)[-1].lower()
        if suffix == "txt":
            return FileLoader._load_txt(file_path)
        if suffix == "pdf":
            return FileLoader._load_pdf(file_path)
        if suffix == "docx":
            return FileLoader._load_docx(file_path)
        raise ValueError("仅支持 txt、pdf、docx 文件")

    @staticmethod
    def _load_txt(file_path):
        """读取 txt 文本文件。"""
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    @staticmethod
    def _load_pdf(file_path):
        """读取 pdf 文件中的文本。"""
        reader = PdfReader(file_path)
        texts = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")
        return "\n".join(texts)

    @staticmethod
    def _load_docx(file_path):
        """读取 docx 文件中的段落文本。"""
        doc = DocxDocument(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QTextEdit, QLabel, QSplitter)
from PySide6.QtCore import Qt

# Add current directory to path so modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.editor import CodeEditor
from ui.syntax_highlighter import PseudocodeHighlighter
from ui.ast_viewer import ASTViewer
from parser.parser import parser
from semantic.semantic_analyzer import SemanticAnalyzer
from translator.python_generator import PythonGenerator
from ai.error_explainer import explain_error

class IDEWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Traductor Educativo - Lenguajes y Autómatas II")
        self.resize(1200, 800)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Toolbar
        toolbar = QHBoxLayout()
        self.btn_analyze = QPushButton("Analizar y Traducir")
        self.btn_explain = QPushButton("Explicar Error con Gemini")
        self.btn_clear = QPushButton("Limpiar")
        
        toolbar.addWidget(self.btn_analyze)
        toolbar.addWidget(self.btn_explain)
        toolbar.addWidget(self.btn_clear)
        layout.addLayout(toolbar)
        
        # Splitter for panels
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel: Editor
        editor_layout = QVBoxLayout()
        editor_widget = QWidget()
        editor_widget.setLayout(editor_layout)
        editor_layout.addWidget(QLabel("Código Fuente (Pseudocódigo):"))
        self.editor = CodeEditor()
        self.highlighter = PseudocodeHighlighter(self.editor.document())
        self.editor.setPlainText("INICIO\nENTERO x = 10\nENTERO y = 5\nMOSTRAR x + y\nFIN")
        editor_layout.addWidget(self.editor)
        splitter.addWidget(editor_widget)
        
        # Middle panel: AST and Translated Code
        middle_layout = QVBoxLayout()
        middle_widget = QWidget()
        middle_widget.setLayout(middle_layout)
        
        middle_layout.addWidget(QLabel("Código Traducido (Python):"))
        self.translated_code = QTextEdit()
        self.translated_code.setReadOnly(True)
        middle_layout.addWidget(self.translated_code)
        
        middle_layout.addWidget(QLabel("Árbol de Sintaxis Abstracta (AST):"))
        self.ast_viewer = ASTViewer()
        middle_layout.addWidget(self.ast_viewer)
        
        splitter.addWidget(middle_widget)
        
        # Right panel: Console / Errors
        right_layout = QVBoxLayout()
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        right_layout.addWidget(QLabel("Consola / Errores:"))
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        right_layout.addWidget(self.console)
        splitter.addWidget(right_widget)
        
        # Connections
        self.btn_analyze.clicked.connect(self.analyze_code)
        self.btn_clear.clicked.connect(self.clear_all)
        self.btn_explain.clicked.connect(self.explain_current_error)
        
        self.current_error = None

    def analyze_code(self):
        code = self.editor.toPlainText()
        self.console.clear()
        self.translated_code.clear()
        self.ast_viewer.clear()
        self.current_error = None
        
        try:
            # 1. Parse (Lexical & Syntax)
            ast = parser.parse(code)
            if not ast:
                raise Exception("Error de sintaxis: No se pudo generar el AST.")
                
            self.ast_viewer.build_tree(ast)
            
            # 2. Semantic Analysis
            semantic = SemanticAnalyzer()
            errors = semantic.analyze(ast)
            
            if errors:
                error_text = "\n".join(errors)
                self.console.setPlainText(f"Errores Semánticos:\n{error_text}")
                self.current_error = error_text
                return
                
            # 3. Code Generation
            generator = PythonGenerator()
            python_code = generator.generate(ast)
            self.translated_code.setPlainText(python_code)
            self.console.setPlainText("Análisis y traducción exitosos.")
            
        except Exception as e:
            self.console.setPlainText(f"Error:\n{str(e)}")
            self.current_error = str(e)

    def explain_current_error(self):
        if not self.current_error:
            self.console.append("\nNo hay errores para explicar.")
            return
            
        self.console.append("\nConsultando a Gemini...")
        QApplication.processEvents()
        
        code = self.editor.toPlainText()
        explanation = explain_error(self.current_error, code)
        self.console.append(f"\n--- Explicación de Gemini ---\n{explanation}")

    def clear_all(self):
        self.editor.clear()
        self.translated_code.clear()
        self.console.clear()
        self.ast_viewer.clear()
        self.current_error = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IDEWindow()
    window.show()
    sys.exit(app.exec())

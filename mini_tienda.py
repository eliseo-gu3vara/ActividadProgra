import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QListWidget, QMessageBox, QSpinBox, QInputDialog
)
from PyQt5.QtGui import QIcon


class InventarioApp(QWidget):
    def __init__(self):
        super().__init__()
        # Configuración básica de la ventana principal
        self.setWindowTitle("Tienda Don Pancho")
        self.resize(500, 420)
        self.setWindowIcon(QIcon("logo.png"))

        # Cargar productos desde archivo JSON
        self.productos = self.cargar_productos()

        # Etiqueta y lista principal de productos disponibles
        self.label = QLabel("Selecciona un producto:")
        self.lista_productos = QListWidget()
        for producto, precio in self.productos.items():
            self.lista_productos.addItem(f"{producto} - ${precio:.2f}")

        # Botón para mostrar formulario de agregar productos
        self.agregar_producto_button = QPushButton("Agregar productos")
        self.agregar_producto_button.clicked.connect(self.mostrar_formulario_agregar)

        # Formulario oculto para agregar nuevos productos
        self.formulario_widget = QWidget()
        self.formulario_layout = QHBoxLayout()
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del producto")
        self.precio_input = QLineEdit()
        self.precio_input.setPlaceholderText("Precio")
        self.guardar_producto_button = QPushButton("Guardar producto")
        self.guardar_producto_button.clicked.connect(self.guardar_producto)
        self.formulario_layout.addWidget(QLabel("Nombre:"))
        self.formulario_layout.addWidget(self.nombre_input)
        self.formulario_layout.addWidget(QLabel("Precio:"))
        self.formulario_layout.addWidget(self.precio_input)
        self.formulario_layout.addWidget(self.guardar_producto_button)
        self.formulario_widget.setLayout(self.formulario_layout)
        self.formulario_widget.hide()  # Se oculta al inicio

        # Botones para modificar o eliminar productos
        self.editar_button = QPushButton("Modificar producto")
        self.editar_button.clicked.connect(self.modificar_producto)
        self.eliminar_button = QPushButton("Eliminar producto")
        self.eliminar_button.clicked.connect(self.eliminar_producto_inventario)

        # Campo de búsqueda
        self.buscar_label = QLabel("Buscar producto:")
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Escribe el nombre del producto...")
        self.buscar_input.textChanged.connect(self.buscar_producto)

        # Etiqueta de precio unitario (cambia al seleccionar un producto)
        self.precio_unitario_label = QLabel("Precio unitario: $0.00")

        # Selector de cantidad (QSpinBox)
        self.cantidad_label = QLabel("Cantidad:")
        self.cantidad_input = QSpinBox()
        self.cantidad_input.setMinimum(1)
        self.cantidad_input.setMaximum(1000)

        # Botones del carrito de compras
        self.add_button = QPushButton("Agregar al carrito")
        self.delete_button = QPushButton("Eliminar del carrito")
        self.recibo_button = QPushButton("Generar recibo")

        # Carrito de compras (lista de productos agregados)
        self.carrito = QListWidget()
        self.total_label = QLabel("Total: $0.00")

        # Layout para cantidad + botón de agregar
        cantidad_layout = QHBoxLayout()
        cantidad_layout.addWidget(self.cantidad_label)
        cantidad_layout.addWidget(self.cantidad_input)
        cantidad_layout.addWidget(self.add_button)

        # Layout para botones del carrito
        botones_layout = QHBoxLayout()
        botones_layout.addWidget(self.delete_button)
        botones_layout.addWidget(self.recibo_button)

        # Layout para botones de productos
        botones_productos_layout = QHBoxLayout()
        botones_productos_layout.addWidget(self.agregar_producto_button)
        botones_productos_layout.addWidget(self.editar_button)
        botones_productos_layout.addWidget(self.eliminar_button)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.lista_productos)
        main_layout.addWidget(self.formulario_widget)
        main_layout.addLayout(botones_productos_layout)
        main_layout.addWidget(self.precio_unitario_label)
        main_layout.addWidget(self.buscar_label)
        main_layout.addWidget(self.buscar_input)
        main_layout.addLayout(cantidad_layout)
        main_layout.addWidget(QLabel("Carrito de compras:"))
        main_layout.addWidget(self.carrito)
        main_layout.addLayout(botones_layout)
        main_layout.addWidget(self.total_label)
        self.setLayout(main_layout)

        # Variables internas para el carrito
        self.total = 0.0
        self.carrito_items = []

        # Conexiones de eventos
        self.lista_productos.currentItemChanged.connect(self.mostrar_precio_unitario)
        self.add_button.clicked.connect(self.agregar_producto)
        self.delete_button.clicked.connect(self.eliminar_producto)
        self.recibo_button.clicked.connect(self.generar_recibo)

    # --- Funciones ---

    def mostrar_formulario_agregar(self):
        """Muestra el formulario para agregar productos nuevos"""
        self.formulario_widget.show()

    def cargar_productos(self):
        """Carga los productos desde el archivo JSON"""
        ruta = os.path.join(os.path.dirname(__file__), "productos.json")
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def guardar_productos_archivo(self):
        """Guarda el diccionario de productos en un archivo JSON"""
        ruta = os.path.join(os.path.dirname(__file__), "productos.json")
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(self.productos, f, ensure_ascii=False, indent=4)

    def guardar_producto(self):
        """Agrega un nuevo producto al inventario"""
        nombre = self.nombre_input.text().strip()
        try:
            precio = float(self.precio_input.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "El precio debe ser un número válido.")
            return

        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre no puede estar vacío.")
            return
        if nombre in self.productos:
            QMessageBox.warning(self, "Error", "El producto ya existe.")
            return

        # Guardar producto
        self.productos[nombre] = precio
        self.lista_productos.addItem(f"{nombre} - ${precio:.2f}")
        # Ocultar formulario y limpiar campos
        self.formulario_widget.hide()
        self.nombre_input.clear()
        self.precio_input.clear()
        # Guardar cambios en archivo
        self.guardar_productos_archivo()

    def modificar_producto(self):
        """Permite editar el nombre y precio de un producto existente"""
        item = self.lista_productos.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Selecciona un producto para modificar.")
            return
        producto = item.text().split(" - ")[0]
        precio = self.productos[producto]

        # Pedir nuevo nombre y precio
        nuevo_nombre, ok1 = QInputDialog.getText(self, "Modificar nombre", "Nuevo nombre:", text=producto)
        if not ok1 or not nuevo_nombre.strip():
            return
        nuevo_precio, ok2 = QInputDialog.getDouble(self, "Modificar precio", "Nuevo precio:", value=precio, min=0.01)
        if not ok2:
            return

        # Validar que no se repita el nombre
        if nuevo_nombre != producto and nuevo_nombre in self.productos:
            QMessageBox.warning(self, "Error", "Ya existe un producto con ese nombre.")
            return

        # Reemplazar producto
        del self.productos[producto]
        self.productos[nuevo_nombre] = nuevo_precio
        self.actualizar_lista_productos()
        self.guardar_productos_archivo()

    def eliminar_producto_inventario(self):
        """Elimina un producto del inventario"""
        item = self.lista_productos.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Selecciona un producto para eliminar.")
            return
        producto = item.text().split(" - ")[0]
        confirm = QMessageBox.question(self, "Eliminar", f"¿Seguro que deseas eliminar '{producto}'?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            del self.productos[producto]
            self.actualizar_lista_productos()
            self.guardar_productos_archivo()

    def actualizar_lista_productos(self):
        """Refresca la lista de productos en pantalla"""
        self.lista_productos.clear()
        for producto, precio in self.productos.items():
            self.lista_productos.addItem(f"{producto} - ${precio:.2f}")

    def mostrar_precio_unitario(self, current, previous):
        """Muestra el precio unitario del producto seleccionado"""
        if current:
            producto = current.text().split(" - ")[0]
            precio = self.productos.get(producto, 0.0)
            self.precio_unitario_label.setText(f"Precio unitario: ${precio:.2f}")
        else:
            self.precio_unitario_label.setText("Precio unitario: $0.00")

    def buscar_producto(self):
        """Filtra productos según el texto escrito en el buscador"""
        texto = self.buscar_input.text().lower()
        self.lista_productos.clear()
        for producto, precio in self.productos.items():
            if texto in producto.lower():
                self.lista_productos.addItem(f"{producto} - ${precio:.2f}")

    def agregar_producto(self):
        """Agrega un producto seleccionado al carrito de compras"""
        item = self.lista_productos.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Selecciona un producto primero.")
            return

        producto = item.text().split(" - ")[0]
        precio_unitario = self.productos[producto]
        cantidad = self.cantidad_input.value()
        subtotal = round(precio_unitario * cantidad, 2)

        # Agregar al carrito
        self.carrito.addItem(f"{producto} x{cantidad} - ${subtotal:.2f}")
        self.carrito_items.append((producto, cantidad, subtotal))

        # Actualizar total
        self.total = round(self.total + subtotal, 2)
        self.total_label.setText(f"Total: ${self.total:.2f}")
        self.cantidad_input.setValue(1)

    def eliminar_producto(self):
        """Elimina un producto seleccionado del carrito"""
        idx = self.carrito.currentRow()
        if idx >= 0:
            _, _, subtotal = self.carrito_items.pop(idx)
            self.total = round(self.total - subtotal, 2)
            self.carrito.takeItem(idx)
            self.total_label.setText(f"Total: ${self.total:.2f}")
        else:
            QMessageBox.warning(self, "Error", "Selecciona un producto del carrito para eliminar.")

    def generar_recibo(self):
        """Genera un recibo con los productos del carrito"""
        if not self.carrito_items:
            QMessageBox.warning(self, "Error", "El carrito está vacío.")
            return

        recibo = "----- RECIBO DE COMPRA -----\n\nItems:\n"
        for producto, cantidad, subtotal in self.carrito_items:
            recibo += f"{producto} x{cantidad} = ${subtotal:.2f}\n"
        recibo += "----------------------------\n"
        recibo += f"TOTAL: ${self.total:.2f}"

        QMessageBox.information(self, "Recibo", recibo)


# Punto de entrada principal
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = InventarioApp()
    ventana.show()
    sys.exit(app.exec_())

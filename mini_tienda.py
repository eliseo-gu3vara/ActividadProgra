# Importamos la librería sys para manejar la ejecución del programa
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QListWidget, QMessageBox, QSpinBox
    # Importa los widgets principales de PyQt5 que permiten crear ventanas, 
    # botones, listas, campos de texto y organizar los elementos en la interfaz
)
from PyQt5.QtGui import QIcon # Permite usar iconos en la ventana o botones


class InventarioApp(QWidget):
    def __init__(self):
        super().__init__()
        # --- Configuración básica de la ventana ---
        self.setWindowTitle("Mini Inventario - Tienda")
        self.setGeometry(200, 200, 500, 420)
        self.setWindowIcon(QIcon("logo.png"))  # Opcional, si tienes logo.png

        # --- Inventario de productos con precios unitarios ---
        self.productos = {
            "Pan": 0.50,
            "Leche": 1.20,
            "Huevos (docena)": 2.50,
            "Arroz (1kg)": 1.00,
            "Café (250g)": 3.00,
            "Azúcar (1kg)": 0.90,
            "Mantequilla": 1.50,
            "Queso (500g)": 2.80
        }

        # --- Widgets básicos ---
        self.label = QLabel("Selecciona un producto:")  # Etiqueta para la lista
        self.lista_productos = QListWidget()            # Lista de productos
        for producto, precio in self.productos.items():
            self.lista_productos.addItem(f"{producto} - ${precio:.2f}")

        # Campo de búsqueda (QLineEdit) para encontrar productos rápidamente
        self.buscar_label = QLabel("Buscar producto:")
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Escribe el nombre del producto...")

        # Mostrar precio unitario del producto seleccionado
        self.precio_unitario_label = QLabel("Precio unitario: $0.00")

        # Cantidad a comprar (QSpinBox)
        self.cantidad_label = QLabel("Cantidad:")
        self.cantidad_input = QSpinBox()
        self.cantidad_input.setMinimum(1)
        self.cantidad_input.setMaximum(1000)

        # Botones de acciones
        self.add_button = QPushButton("Agregar al carrito")
        self.delete_button = QPushButton("Eliminar del carrito")
        self.recibo_button = QPushButton("Generar recibo")

        # Carrito (QListWidget) y total
        self.carrito = QListWidget()
        self.total_label = QLabel("Total: $0.00")

        # --- Layouts (organización de widgets en pantalla) ---
        cantidad_layout = QHBoxLayout()
        cantidad_layout.addWidget(self.cantidad_label)
        cantidad_layout.addWidget(self.cantidad_input)
        cantidad_layout.addWidget(self.add_button)

        botones_layout = QHBoxLayout()
        botones_layout.addWidget(self.delete_button)
        botones_layout.addWidget(self.recibo_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.lista_productos)
        main_layout.addWidget(self.precio_unitario_label)
        main_layout.addWidget(self.buscar_label)
        main_layout.addWidget(self.buscar_input)
        main_layout.addLayout(cantidad_layout)
        main_layout.addWidget(QLabel("Carrito de compras:"))
        main_layout.addWidget(self.carrito)
        main_layout.addLayout(botones_layout)
        main_layout.addWidget(self.total_label)

        self.setLayout(main_layout)

        # --- Variables internas ---
        self.total = 0.0
        self.carrito_items = []  # Lista paralela con (producto, cantidad, subtotal)

        # --- Conexiones (eventos) ---
        self.lista_productos.currentItemChanged.connect(self.mostrar_precio_unitario)
        self.buscar_input.textChanged.connect(self.buscar_producto)
        self.add_button.clicked.connect(self.agregar_producto)
        self.delete_button.clicked.connect(self.eliminar_producto)
        self.recibo_button.clicked.connect(self.generar_recibo)

    # --- Funciones ---
    def mostrar_precio_unitario(self, current, previous):
        """Muestra el precio unitario del producto seleccionado en la lista."""
        if current:
            producto = current.text().split(" - ")[0]
            precio = self.productos.get(producto, 0.0)
            self.precio_unitario_label.setText(f"Precio unitario: ${precio:.2f}")
        else:
            self.precio_unitario_label.setText("Precio unitario: $0.00")

    def buscar_producto(self):
        """Filtra los productos en la lista según lo escrito en el QLineEdit."""
        texto = self.buscar_input.text().lower()
        self.lista_productos.clear()
        for producto, precio in self.productos.items():
            if texto in producto.lower():
                self.lista_productos.addItem(f"{producto} - ${precio:.2f}")

    def agregar_producto(self):
        """Agrega el producto seleccionado al carrito con su cantidad y subtotal."""
        item = self.lista_productos.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Selecciona un producto primero.")
            return

        producto = item.text().split(" - ")[0]
        precio_unitario = self.productos[producto]
        cantidad = self.cantidad_input.value()
        subtotal = round(precio_unitario * cantidad, 2)

        # Agregar al carrito (interfaz y lista interna)
        self.carrito.addItem(f"{producto} x{cantidad} - ${subtotal:.2f}")
        self.carrito_items.append((producto, cantidad, subtotal))

        # Actualizar total
        self.total = round(self.total + subtotal, 2)
        self.total_label.setText(f"Total: ${self.total:.2f}")

        # Resetear cantidad
        self.cantidad_input.setValue(1)

    def eliminar_producto(self):
        """Elimina el producto seleccionado del carrito y resta su subtotal del total."""
        idx = self.carrito.currentRow()
        if idx >= 0:
            _, _, subtotal = self.carrito_items.pop(idx)
            self.total = round(self.total - subtotal, 2)
            self.carrito.takeItem(idx)
            self.total_label.setText(f"Total: ${self.total:.2f}")
        else:
            QMessageBox.warning(self, "Error", "Selecciona un producto del carrito para eliminar.")

    def generar_recibo(self):
        """Genera un recibo con los productos en el carrito y el total a pagar."""
        if not self.carrito_items:
            QMessageBox.warning(self, "Error", "El carrito está vacío.")
            return

        recibo = "----- RECIBO DE COMPRA -----\n\nItems:\n"
        for producto, cantidad, subtotal in self.carrito_items:
            recibo += f"{producto} x{cantidad} = ${subtotal:.2f}\n"
        recibo += "----------------------------\n"
        recibo += f"TOTAL A PAGAR: ${self.total:.2f}"

        QMessageBox.information(self, "Recibo", recibo)


# --- Ejecución del programa ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = InventarioApp()
    ventana.show()
    sys.exit(app.exec_())

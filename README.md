# ChinaWok - Sistema de Gestión de Pedidos

## 📋 Descripción

Sistema CRUD para la gestión de pedidos, productos, combos y ofertas de ChinaWok utilizando AWS Lambda y DynamoDB.

## 🏗️ Estructura del Proyecto

```
Chinawok-Pedidos/
├── Combos/
│   ├── create.py       # Crear combos
│   ├── read.py         # Leer combos
│   ├── update.py       # Actualizar combos
│   └── delete.py       # Eliminar combos
├── Ofertas/
│   ├── create.py       # Crear ofertas
│   ├── read.py         # Leer ofertas
│   ├── update.py       # Actualizar ofertas
│   └── delete.py       # Eliminar ofertas
├── Pedido/
│   ├── create.py       # Crear pedidos
│   ├── read.py         # Leer pedidos
│   ├── update.py       # Actualizar pedidos
│   └── delete.py       # Eliminar pedidos
├── Producto/
│   ├── create.py       # Crear productos
│   ├── read.py         # Leer productos
│   ├── update.py       # Actualizar productos
│   └── delete.py       # Eliminar productos
├── requirements.txt    # Dependencias Python
├── serverless.yml      # Configuración Serverless Framework
└── .env.example        # Variables de entorno de ejemplo
```

## 📊 Tablas de DynamoDB

### 1. Combos (ChinaWok-Combos)
- **Partition Key**: `local_id`
- **Sort Key**: `combo_id`
- **Atributos**: nombre, productos_nombres[], descripcion

### 2. Ofertas (ChinaWok-Ofertas)
- **Partition Key**: `local_id`
- **Sort Key**: `oferta_id`
- **Atributos**: producto_nombre/combo_id, fecha_inicio, fecha_limite, porcentaje_descuento

### 3. Pedidos (ChinaWok-Pedidos)
- **Partition Key**: `local_id`
- **Sort Key**: `pedido_id`
- **Atributos**: usuario_correo, productos_nombres[], costo, direccion, estado, historial_estados[]

### 4. Productos (ChinaWok-Productos)
- **Partition Key**: `local_id`
- **Sort Key**: `nombre`
- **Atributos**: precio, descripcion, categoria, stock

## 🚀 Instalación

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd Chinawok-Pedidos
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales de AWS
```

4. Desplegar con Serverless Framework:
```bash
serverless deploy
```

## 📝 Uso de las APIs

### Combos

#### Crear Combo
```bash
POST /combos
Body: {
  "local_id": "LOCAL001",
  "combo_id": "COMBO001",
  "nombre": "Combo Familiar",
  "productos_nombres": ["Arroz Chaufa", "Tallarín Saltado"],
  "descripcion": "Combo para 4 personas"
}
```

#### Leer Combos
```bash
# Todos los combos de un local
GET /combos?local_id=LOCAL001

# Un combo específico
GET /combos?local_id=LOCAL001&combo_id=COMBO001
```

#### Actualizar Combo
```bash
PUT /combos
Body: {
  "local_id": "LOCAL001",
  "combo_id": "COMBO001",
  "nombre": "Combo Familiar Plus",
  "descripcion": "Ahora con más opciones"
}
```

#### Eliminar Combo
```bash
DELETE /combos?local_id=LOCAL001&combo_id=COMBO001
```

### Ofertas

#### Crear Oferta
```bash
POST /ofertas
Body: {
  "local_id": "LOCAL001",
  "oferta_id": "OFERTA001",
  "producto_nombre": "Arroz Chaufa",
  "fecha_inicio": "2024-01-01T00:00:00Z",
  "fecha_limite": "2024-01-31T23:59:59Z",
  "porcentaje_descuento": 20
}
```

#### Leer Ofertas
```bash
# Todas las ofertas de un local
GET /ofertas?local_id=LOCAL001

# Una oferta específica
GET /ofertas?local_id=LOCAL001&oferta_id=OFERTA001
```

#### Actualizar Oferta
```bash
PUT /ofertas
Body: {
  "local_id": "LOCAL001",
  "oferta_id": "OFERTA001",
  "porcentaje_descuento": 25
}
```

#### Eliminar Oferta
```bash
DELETE /ofertas?local_id=LOCAL001&oferta_id=OFERTA001
```

### Pedidos

#### Crear Pedido
```bash
POST /pedidos
Body: {
  "local_id": "LOCAL001",
  "pedido_id": "PEDIDO001",
  "usuario_correo": "cliente@example.com",
  "productos_nombres": ["Arroz Chaufa", "Wantán Frito"],
  "costo": 35.50,
  "direccion": "Av. Principal 123",
  "estado": "procesando",
  "historial_estados": [
    {
      "estado": "procesando",
      "hora_inicio": "2024-01-15T12:00:00Z",
      "hora_fin": "2024-01-15T12:00:00Z",
      "activo": true,
      "empleado": null
    }
  ]
}
```

#### Leer Pedidos
```bash
# Todos los pedidos de un local
GET /pedidos?local_id=LOCAL001

# Un pedido específico
GET /pedidos?local_id=LOCAL001&pedido_id=PEDIDO001
```

#### Actualizar Pedido
```bash
PUT /pedidos
Body: {
  "local_id": "LOCAL001",
  "pedido_id": "PEDIDO001",
  "estado": "cocinando",
  "historial_estados": [...]
}
```

#### Eliminar Pedido
```bash
DELETE /pedidos?local_id=LOCAL001&pedido_id=PEDIDO001
```

### Productos

#### Crear Producto
```bash
POST /productos
Body: {
  "local_id": "LOCAL001",
  "nombre": "Arroz Chaufa",
  "precio": 18.50,
  "descripcion": "Arroz frito al estilo chino",
  "categoria": "Arroces",
  "stock": 100
}
```

#### Leer Productos
```bash
# Todos los productos de un local
GET /productos?local_id=LOCAL001

# Un producto específico
GET /productos?local_id=LOCAL001&nombre=Arroz%20Chaufa
```

#### Actualizar Producto
```bash
PUT /productos
Body: {
  "local_id": "LOCAL001",
  "nombre": "Arroz Chaufa",
  "precio": 19.50,
  "stock": 95
}
```

#### Eliminar Producto
```bash
DELETE /productos?local_id=LOCAL001&nombre=Arroz%20Chaufa
```

## 📚 Validación de Schemas

Todos los endpoints validan los datos usando JSON Schema para garantizar la integridad de los datos:

- ✅ Validación de tipos de datos
- ✅ Validación de campos requeridos
- ✅ Validación de enums (estados, categorías, roles)
- ✅ Validación de rangos (precios, descuentos, calificaciones)
- ✅ Validación de formatos (emails, fechas)

## 🔒 Seguridad

- Las funciones Lambda utilizan el rol IAM `LabRole`
- CORS habilitado en todos los endpoints
- Validación de entrada para prevenir inyecciones
- Manejo centralizado de errores

## 📊 Categorías de Productos

- Arroces
- Tallarines
- Pollo al wok
- Carne de res
- Cerdo
- Mariscos
- Entradas
- Guarniciones
- Sopas
- Combos
- Bebidas
- Postres

## 🔄 Estados de Pedidos

1. **procesando** - Pedido recibido
2. **cocinando** - En preparación
3. **empacando** - Siendo empacado
4. **enviando** - En camino
5. **recibido** - Entregado

## 👥 Roles de Empleados

- **cocinero** - Prepara los alimentos
- **despachador** - Empaca los pedidos
- **repartidor** - Entrega los pedidos

## 🛠️ Dependencias

- `boto3`: SDK de AWS para Python
- `jsonschema`: Validación de esquemas JSON

## 📄 Licencia

Propiedad de ChinaWok Perú

## 👨‍💻 Autor

Desarrollado para ChinaWok Perú

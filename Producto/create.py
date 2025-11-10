import json
import boto3
import os
from jsonschema import validate, ValidationError

# Cliente DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_PRODUCTOS', 'ChinaWok-Productos')
table = dynamodb.Table(table_name)

# Schema de validación
PRODUCTO_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Productos",
    "type": "object",
    "properties": {
        "local_id": {"type": "string"},
        "nombre": {"type": "string", "minLength": 1},
        "precio": {"type": "number", "minimum": 0},
        "descripcion": {"type": "string"},
        "categoria": {
            "type": "string",
            "enum": [
                "Arroces",
                "Tallarines",
                "Pollo al wok",
                "Carne de res",
                "Cerdo",
                "Mariscos",
                "Entradas",
                "Guarniciones",
                "Sopas",
                "Combos",
                "Bebidas",
                "Postres"
            ]
        },
        "stock": {"type": "integer", "minimum": 0}
    },
    "required": ["local_id", "nombre", "precio", "categoria", "stock"],
    "additionalProperties": False
}


def handler(event, context):
    """
    Lambda handler para crear un producto en DynamoDB
    """
    try:
        # Parsear el body del evento
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)
        
        # Validar schema
        validate(instance=body, schema=PRODUCTO_SCHEMA)
        
        # Insertar en DynamoDB
        table.put_item(Item=body)
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Producto creado exitosamente',
                'data': body
            })
        }
        
    except ValidationError as e:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Error de validación',
                'message': str(e.message)
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Error interno del servidor',
                'message': str(e)
            })
        }

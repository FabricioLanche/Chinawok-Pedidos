import json
import boto3
import os
from jsonschema import validate, ValidationError

# Cliente DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_OFERTAS', 'ChinaWok-Ofertas')
table = dynamodb.Table(table_name)

# Schema de validación
OFERTA_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Ofertas",
    "type": "object",
    "properties": {
        "local_id": {"type": "string"},
        "oferta_id": {"type": "string"},
        "producto_nombre": {"type": "string"},
        "combo_id": {"type": "string"},
        "fecha_inicio": {"type": "string", "format": "date-time"},
        "fecha_limite": {"type": "string", "format": "date-time"},
        "porcentaje_descuento": {"type": "number", "minimum": 0, "maximum": 100}
    },
    "required": ["local_id", "oferta_id", "porcentaje_descuento", "fecha_inicio", "fecha_limite"],
    "additionalProperties": False,
    "anyOf": [
        {"required": ["producto_nombre"]},
        {"required": ["combo_id"]}
    ]
}


def handler(event, context):
    """
    Lambda handler para crear una oferta en DynamoDB
    """
    try:
        # Parsear el body del evento
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)
        
        # Validar schema
        validate(instance=body, schema=OFERTA_SCHEMA)
        
        # Validar que tenga producto_nombre o combo_id
        if 'producto_nombre' not in body and 'combo_id' not in body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Debe especificar producto_nombre o combo_id'
                })
            }
        
        # Insertar en DynamoDB
        table.put_item(Item=body)
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Oferta creada exitosamente',
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

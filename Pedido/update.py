import json
import boto3
import os
from jsonschema import validate, ValidationError

# Cliente DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_PEDIDOS', 'ChinaWok-Pedidos')
table = dynamodb.Table(table_name)

# Schema de validación (sin requerir todas las propiedades para update parcial)
PEDIDO_UPDATE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "PedidosUpdate",
    "type": "object",
    "properties": {
        "productos_nombres": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        },
        "costo": {"type": "number", "minimum": 0},
        "direccion": {"type": "string"},
        "fecha_entrega_aproximada": {
            "type": ["string", "null"],
            "format": "date-time"
        },
        "estado": {
            "type": "string",
            "enum": ["procesando", "cocinando", "empacando", "enviando", "recibido"]
        },
        "historial_estados": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "estado": {
                        "type": "string",
                        "enum": ["procesando", "cocinando", "empacando", "enviando", "recibido"]
                    },
                    "hora_inicio": {"type": "string", "format": "date-time"},
                    "hora_fin": {"type": "string", "format": "date-time"},
                    "activo": {"type": "boolean"},
                    "empleado": {
                        "type": ["object", "null"],
                        "properties": {
                            "dni": {"type": "string"},
                            "nombre_completo": {"type": "string"},
                            "rol": {
                                "type": "string",
                                "enum": ["cocinero", "despachador", "repartidor"]
                            },
                            "calificacion_prom": {"type": "number", "minimum": 0, "maximum": 5}
                        },
                        "required": ["dni", "nombre_completo", "rol"]
                    }
                },
                "required": ["estado", "hora_inicio", "hora_fin", "activo"]
            },
            "minItems": 1
        }
    },
    "additionalProperties": False,
    "minProperties": 1
}


def handler(event, context):
    """
    Lambda handler para actualizar un pedido en DynamoDB
    """
    try:
        # Parsear el body del evento
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)
        
        # Obtener las keys
        local_id = body.get('local_id')
        pedido_id = body.get('pedido_id')
        
        if not local_id or not pedido_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Se requieren local_id y pedido_id'
                })
            }
        
        # Crear una copia sin las keys para validar solo los campos actualizables
        update_data = {k: v for k, v in body.items() if k not in ['local_id', 'pedido_id', 'usuario_correo']}
        
        if not update_data:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'No se proporcionaron campos para actualizar'
                })
            }
        
        # Validar schema
        validate(instance=update_data, schema=PEDIDO_UPDATE_SCHEMA)
        
        # Construir expresión de actualización
        update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in update_data.keys()])
        expression_attribute_names = {f"#{k}": k for k in update_data.keys()}
        expression_attribute_values = {f":{k}": v for k, v in update_data.items()}
        
        # Actualizar en DynamoDB
        response = table.update_item(
            Key={
                'local_id': local_id,
                'pedido_id': pedido_id
            },
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW"
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Pedido actualizado exitosamente',
                'data': response['Attributes']
            }, default=str)
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

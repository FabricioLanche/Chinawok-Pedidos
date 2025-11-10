import json
import boto3
import os
from jsonschema import validate, ValidationError

# Cliente DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_OFERTAS', 'ChinaWok-Ofertas')
table = dynamodb.Table(table_name)

# Schema de validación (sin requerir todas las propiedades para update parcial)
OFERTA_UPDATE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "OfertasUpdate",
    "type": "object",
    "properties": {
        "producto_nombre": {"type": "string"},
        "combo_id": {"type": "string"},
        "fecha_inicio": {"type": "string", "format": "date-time"},
        "fecha_limite": {"type": "string", "format": "date-time"},
        "porcentaje_descuento": {"type": "number", "minimum": 0, "maximum": 100}
    },
    "additionalProperties": False,
    "minProperties": 1
}


def handler(event, context):
    """
    Lambda handler para actualizar una oferta en DynamoDB
    """
    try:
        # Parsear el body del evento
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)
        
        # Obtener las keys
        local_id = body.get('local_id')
        oferta_id = body.get('oferta_id')
        
        if not local_id or not oferta_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Se requieren local_id y oferta_id'
                })
            }
        
        # Crear una copia sin las keys para validar solo los campos actualizables
        update_data = {k: v for k, v in body.items() if k not in ['local_id', 'oferta_id']}
        
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
        validate(instance=update_data, schema=OFERTA_UPDATE_SCHEMA)
        
        # Construir expresión de actualización
        update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in update_data.keys()])
        expression_attribute_names = {f"#{k}": k for k in update_data.keys()}
        expression_attribute_values = {f":{k}": v for k, v in update_data.items()}
        
        # Actualizar en DynamoDB
        response = table.update_item(
            Key={
                'local_id': local_id,
                'oferta_id': oferta_id
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
                'message': 'Oferta actualizada exitosamente',
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

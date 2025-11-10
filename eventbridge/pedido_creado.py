import json
import os
import boto3
from datetime import datetime

# Clientes AWS
stepfunctions = boto3.client('stepfunctions')

def handler(event, context):
    """
    Handler para procesar eventos de pedido creado desde EventBridge
    y ejecutar el Step Function correspondiente.
    """
    try:
        print(f"Evento recibido: {json.dumps(event)}")
        
        # Construir el ARN del Step Function dinámicamente
        aws_account_id = os.environ.get('AWS_ACCOUNT_ID')
        aws_region = os.environ.get('AWS_REGION', 'us-east-1')
        step_function_name = os.environ.get('STEP_FUNCTION_PEDIDOS_NAME')
        
        if not aws_account_id or not step_function_name:
            raise ValueError("AWS_ACCOUNT_ID o STEP_FUNCTION_PEDIDOS_NAME no configurados")
        
        # Construir ARN: arn:aws:states:region:account-id:stateMachine:name
        step_function_arn = f"arn:aws:states:{aws_region}:{aws_account_id}:stateMachine:{step_function_name}"
        
        print(f"Step Function ARN construido: {step_function_arn}")
        
        # Extraer datos del pedido desde el evento
        pedido_data = event.get('detail', {})
        
        if not pedido_data:
            raise ValueError("No se encontraron datos del pedido en el evento")
        
        # Preparar input para el Step Function
        step_function_input = {
            'pedido': pedido_data,
            'timestamp': datetime.utcnow().isoformat(),
            'eventId': event.get('id'),
            'source': event.get('source')
        }
        
        # Ejecutar el Step Function
        response = stepfunctions.start_execution(
            stateMachineArn=step_function_arn,
            input=json.dumps(step_function_input),
            name=f"pedido-{pedido_data.get('id_pedido', 'unknown')}-{int(datetime.utcnow().timestamp())}"
        )
        
        print(f"Step Function iniciado: {response['executionArn']}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Pedido enviado a Step Function exitosamente',
                'executionArn': response['executionArn'],
                'pedidoId': pedido_data.get('id_pedido')
            })
        }
        
    except Exception as e:
        print(f"Error procesando evento de pedido creado: {str(e)}")
        raise


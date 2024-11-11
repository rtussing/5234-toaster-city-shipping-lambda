import json

import sqlalchemy as sa

from services.shipping_processing_service import ShippingProcessingService

class OrderProcessingHandler():
    """Handles events (HTTP requests) for the order-processing resource."""
    _engine: sa.engine.Engine
    _processor: ShippingProcessingService

    def __init__(self, engine: sa.engine.Engine):
        """
        Parameters
        ----------
        engine : sqlalchemy.engine.Engine
            The engine to connect to the database with the Inventory information.
        """
        super().__init__()
        self._engine = engine
        self._processor = ShippingProcessingService(self._engine)


    def handle_request(self, event, context) -> tuple[int, dict | str]:
        """Handles requests related to the order-processing resource."""
        path = event['resource']

        if path == '/shipping':
            status_code, body = self.post_order(event['body'])
        else:
            status_code = 400
            body = 'Unknown path for shipping resource.'

        return status_code, body


    def post_shipping(self, shipping) -> tuple[int, str | dict]:
        """
        POST shipping information to the database.

        Parameters
        ----------
        shipping : Any
            The shipping information to be posted.

        Returns
        -------
        tuple[int, str | dict]
            An HTTP status code and a message. If no error, message is confirmation number.
        """
        # Everything is validated by order processing service
        # if not self.__validate_shipping__(shipping):
        #     return 400, 'Order not properly formatted.'

        shipping = json.loads(shipping)
        status_code, msg =  self._processor.process_shipping(shipping)

        if isinstance(msg, int):
            msg = {
                'confirmation_number': msg
            }

        return 200, msg
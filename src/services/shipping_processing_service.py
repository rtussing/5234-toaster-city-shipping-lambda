import pandas as pd
import sqlalchemy as sa
from sqlalchemy.orm import Session

from utils.database_provider import DatabaseProvider
from models.toasterdb_orms import *

class ShippingProcessingService(object):
    """Handles shipping processing for a singular order."""
    _engine: sa.engine.Engine

    _raw_shipping: dict

    _shipping_df: pd.DataFrame = None

    _shipping_info_id: int = None

    def __init__(self, engine: sa.engine.Engine):
        """
        Parameters
        ----------
        db_engine : SQLAlchemy.engine.Engine
            The engine to connect to the database to handle the order.
        """
        self._engine = engine


    def process_shipping(self, shipping: dict) -> tuple[int, str | int]:
        """
        Process shipping information from order. If shipping info does not already exist in database,
        sets `self._shipping_df` with `pandas.DataFrame` of the shipping info. Also sets `self._shipping_info_id`
        with the existing shipping info in database or new one that's going to be inserted.

        Parameters
        ----------
        order : dict
            The shipping information that's to be processed. Expected format of the information:
            ```
            {
                'company_id': 1,
                'number_of_items': 2,
                'approximate_weight': 5.0,
                'name': 'Jane Doe',
                'address_1': '123 Main St',
                'address_2': '321 2nd Ave',
                'city': 'Columbus',
                'state': 'OH',
                'zip': 43210
            }
            ```

        Returns
        -------
        tuple[int, str]
            A an HTTP response status code and a message. If no error, message is confirmation number.
        """
        # Retrieve/calculate new ID for row, since to_sql doesn't return new ID from auto_increment
        id = DatabaseProvider.query_db(self._engine, sa.select(sa.func.ifnull(sa.func.max(ShippingInfo.id), 0) + 1))[0][0]

        # column names are the same as keys in shipment, but uppercase
        self._shipping_df = pd.DataFrame([], columns=[ShippingInfo.id.name] + list(shipping.keys()))
        self._shipping_df.loc[0] = [id] + [str(c) for c in shipping.values()]

        self._shipping_info_id = id

        self._raw_shipping = shipping

        if not self.__update_database_with_shipping__():
            return 500, f'An error occurred when making changes to database.'

        return 200, self._order_id

    def __update_database_with_shipping__(self) -> bool:
        """
        Makes necessary changes to the database based on the shipping information.
        Inserts shipping info if it's new.

        Returns
        -------
        bool
            An indicator of success. True if transaction was success, False otherwise.
        """
        session = Session(self._engine)
        success = True
        with Session(self._engine) as session:
            session.begin()
            try:
                # Shipping may already exist
                if (self._shipping_df is not None and not self._shipping_df.empty):
                    session.execute(sa.insert(ShippingInfo).values(self._shipping_df.to_dict('records')))
            except Exception as err:
                session.rollback()
                success = False
            else:
                session.commit()
        return success

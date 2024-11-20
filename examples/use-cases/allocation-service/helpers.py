import datetime
from collections import defaultdict

from lusid import models


class AllocationServiceHelpers:
    @staticmethod
    def create_order_set_request_from_df(df, scope):
        order_requests = list()

        for index, order in df.iterrows():
            order_requests.append(
                models.OrderRequest(
                    id=models.ResourceId(
                        scope=scope,
                        code=order['order_id']
                    ),
                    quantity=order['quantity'],
                    side=order['side'],
                    instrument_identifiers={
                        'Instrument/default/Figi': order['figi']
                    },
                    properties={},
                    portfolio_id=models.ResourceId(
                        scope=scope,
                        code=order['portfolio']
                    ),
                    state=order['state'],
                    type=order['type'],
                    date=datetime.datetime.fromisoformat(order['date']),
                    price=models.CurrencyAndAmount(amount=order['quantity'], currency=order['currency'])
                )
            )

        return models.OrderSetRequest(order_requests=order_requests)

    @staticmethod
    def create_block_set_request_from_df(df, scope):
        block_requests = list()

        for index, block in df.iterrows():
            order_ids = list()
            for x in block['order_ids'].split(","):
                order_ids.append(models.ResourceId(scope=scope, code=x))

            block_requests.append(
                models.BlockRequest(
                    id=models.ResourceId(
                        scope=scope,
                        code=block['block_id']
                    ),
                    order_ids=order_ids,
                    instrument_identifiers={
                        'Instrument/default/Figi': block['figi']
                    },
                    quantity=block['quantity'],
                    side=block['side'],
                    type=block['type'],
                    time_in_force=block['time_in_force'],
                    created_date=datetime.datetime.fromisoformat(block['created_date'])
                )
            )

        return models.BlockSetRequest(requests=block_requests)

    @staticmethod
    def create_placement_set_request_from_df(df, scope):
        placement_requests = list()

        for index, placement in df.iterrows():
            placement_requests.append(
                models.PlacementRequest(
                    id=models.ResourceId(
                        scope=scope,
                        code=placement['placement_id']
                    ),
                    block_ids=[models.ResourceId(scope=scope, code=placement['block_id'])],
                    instrument_identifiers={
                        'Instrument/default/Figi': placement['figi']
                    },
                    quantity=placement['quantity'],
                    state=placement['state'],
                    side=placement['side'],
                    type=placement['type'],
                    time_in_force=placement['time_in_force'],
                    created_date=datetime.datetime.fromisoformat(placement['created_date'])
                )
            )

        return models.PlacementSetRequest(requests=placement_requests)

    @staticmethod
    def create_execution_set_request_from_df(df, scope):
        execution_requests = list()

        for index, execution in df.iterrows():
            execution_requests.append(
                models.ExecutionRequest(
                    id=models.ResourceId(
                        scope=scope,
                        code=execution['execution_id']
                    ),
                    placement_id=models.ResourceId(
                        scope=scope,
                        code=execution['placement_id']
                    ),
                    instrument_identifiers={
                        'Instrument/default/Figi': execution['figi']
                    },
                    quantity=execution['quantity'],
                    state=execution['state'],
                    side=execution['side'],
                    type=execution['type'],
                    price=models.CurrencyAndAmount(amount=execution['price'], currency=execution['currency']),
                    settlement_currency=execution['settlement_currency'],
                    settlement_currency_fx_rate=execution['settlement_currency_fx_rate'],
                    counterparty=execution['counterparty'],
                    created_date=datetime.datetime.fromisoformat(execution['created_date'])
                )
            )

        return models.ExecutionSetRequest(requests=execution_requests)

    @staticmethod
    def create_allocation_set_request_from_df(df, scope):
        allocation_requests = list()

        for index, allocation in df.iterrows():
            execution_ids = list()
            placement_ids = list()
            for x in allocation['execution_ids'].split(","):
                execution_ids.append(models.ResourceId(scope=scope, code=x))
            for x in allocation['placement_ids'].split(","):
                placement_ids.append(models.ResourceId(scope=scope, code=x))

            allocation_requests.append(
                models.AllocationRequest(
                    instrument_identifiers={
                        'Instrument/default/Figi': allocation['figi']
                    },
                    quantity=allocation['quantity'],
                    portfolio_id=models.ResourceId(
                        scope=scope,
                        code=allocation['portfolio_id']
                    ),
                    allocated_order_id=models.ResourceId(
                        scope=scope,
                        code=allocation['order_id']
                    ),
                    id=models.ResourceId(
                        scope=scope,
                        code=allocation['allocation_id']
                    ),
                    price=models.CurrencyAndAmount(amount=allocation['price'], currency=allocation['currency']),
                    execution_ids=execution_ids,
                    placement_ids=placement_ids,
                    date=datetime.datetime.fromisoformat(allocation['date'])
                )
            )
        return models.AllocationSetRequest(allocation_requests=allocation_requests)

    @staticmethod
    def create_transaction_request_dict_from_df(df, scope):
        txn_requests = defaultdict(list)

        for index, txn in df.iterrows():
            txn_requests[txn['portfolio_id']].append(
                models.TransactionRequest(
                    transaction_id=txn['transaction_id'],
                    type=txn['type'],
                    instrument_identifiers={
                        'Instrument/default/Figi': txn['figi']
                    },
                    transaction_date=txn['transaction_date'],
                    settlement_date=txn['settlement_date'],
                    units=txn['quantity'],
                    transaction_price=models.TransactionPrice(txn['price'], "Price"),
                    total_consideration=models.CurrencyAndAmount(txn['cost'], txn['currency']),
                    order_id=models.ResourceId(
                        scope=scope,
                        code=txn['order_id']
                    ),
                    allocation_id=models.ResourceId(
                        scope=scope,
                        code=txn['allocation_id']
                    )
                )
            )

        return txn_requests

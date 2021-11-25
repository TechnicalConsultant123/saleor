import logging
import os
from unittest.mock import ANY, Mock, patch

import pytest
import requests
from graphene import Node

from saleor.payment import PaymentError


@patch("saleor.payment.gateways.np_atobarai.api_helpers.requests.request")
def test_process_payment_authorized(
    mocked_request, np_atobarai_plugin, np_payment_data
):
    # given
    plugin = np_atobarai_plugin()
    payment_data = np_payment_data
    response = Mock(
        spec=requests.Response,
        status_code=200,
        json=Mock(
            return_value={
                "results": [
                    {
                        "shop_transaction_id": "abc1234567890",
                        "np_transaction_id": "18121200001",
                        "authori_result": "00",
                        "authori_required_date": "2018-12-12T12:00:00+09:00",
                    }
                ]
            }
        ),
    )
    mocked_request.return_value = response

    # when
    gateway_response = plugin.process_payment(payment_data, None)

    # then
    assert gateway_response.is_success
    assert not gateway_response.error


@patch("saleor.payment.gateways.np_atobarai.api_helpers.requests.request")
def test_process_payment_refused(mocked_request, np_atobarai_plugin, np_payment_data):
    # given
    plugin = np_atobarai_plugin()
    payment_data = np_payment_data
    response = Mock(
        spec=requests.Response,
        status_code=200,
        json=Mock(
            return_value={
                "results": [
                    {
                        "shop_transaction_id": "abc1234567890",
                        "np_transaction_id": "18121200001",
                        "authori_result": "20",
                        "authori_required_date": "2018-12-12T12:00:00+09:00",
                    }
                ]
            }
        ),
    )
    mocked_request.return_value = response

    # when
    gateway_response = plugin.process_payment(payment_data, None)

    # then
    assert not gateway_response.is_success


def test_process_payment_no_payment(np_atobarai_plugin, np_payment_data, caplog):
    # given
    plugin = np_atobarai_plugin()
    payment_data = np_payment_data
    payment_data.payment_id = -1

    # when
    with pytest.raises(PaymentError, match=r".*not exist.*"):
        plugin.process_payment(payment_data, None)

    # then
    payment_id = Node.to_global_id("Payment", -1)
    assert caplog.record_tuples == [
        (ANY, logging.ERROR, f"Payment with id {payment_id} does not exist")
    ]


@patch("saleor.payment.gateways.np_atobarai.api_helpers.requests.request")
def test_process_payment_error(mocked_request, np_atobarai_plugin, np_payment_data):
    # given
    plugin = np_atobarai_plugin()
    payment_data = np_payment_data
    error_codes = ["E0100059", "E0100083"]
    response = Mock(
        spec=requests.Response,
        status_code=400,
        json=Mock(return_value={"errors": [{"codes": error_codes}]}),
    )
    mocked_request.return_value = response

    # when
    gateway_response = plugin.process_payment(payment_data, None)

    # then
    assert not gateway_response.is_success
    assert gateway_response.error == os.linesep.join(
        f"TR#{code}" for code in error_codes
    )


def test_capture_payment(np_atobarai_plugin):
    # given
    plugin = np_atobarai_plugin()

    # then
    with pytest.raises(NotImplementedError):
        # when
        plugin.capture_payment(Mock(), None)


def test_void_payment(np_atobarai_plugin):
    # given
    plugin = np_atobarai_plugin()

    # then
    with pytest.raises(NotImplementedError):
        # when
        plugin.void_payment(Mock(), None)

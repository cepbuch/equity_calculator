from decimal import Decimal

from app.core.config import settings
from fastapi.testclient import TestClient


def test_vested_value_one_grant_one_valuation(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 800,
                'start_date': '01-01-2018',
                'cliff_months': 4,
                'duration_months': 8
            }
        ],
        'company_valuations': [
            {
                'price': 10.0,
                'valuation_date': '09-12-2017'
            }
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == [
        {
            'total_value': 0.0,
            'date': '01-01-2018'
        },
        {
            'total_value': 0.0,
            'date': '01-02-2018'
        },
        {
            'total_value': 0.0,
            'date': '01-03-2018'
        },
        {
            'total_value': 0.0,
            'date': '01-04-2018'
        },
        {
            'total_value': 4000.0,
            'date': '01-05-2018'
        },
        {
            'total_value': 5000.0,
            'date': '01-06-2018'
        },
        {
            'total_value': 6000.0,
            'date': '01-07-2018'
        },
        {
            'total_value': 7000.0,
            'date': '01-08-2018'
        },
        {
            'total_value': 8000.0,
            'date': '01-09-2018'
        },
    ]


def test_vested_value_rising_valuation(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 400,
                'start_date': '01-01-2018',
                'cliff_months': 2,
                'duration_months': 4
            }
        ],
        'company_valuations': [
            {
                'price': 10.0,
                'valuation_date': '15-12-2017'
            },
            {
                'price': 15.0,
                'valuation_date': '15-04-2018'
            }
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == [
        {
            'total_value': 0.0,
            'date': '01-01-2018'
        },
        {
            'total_value': 0.0,
            'date': '01-02-2018'
        },
        {
            'total_value': 2000.0,
            'date': '01-03-2018'
        },
        {
            'total_value': 3000.0,
            'date': '01-04-2018'
        },
        {
            'total_value': 6000.0,
            'date': '01-05-2018'
        },
    ]


def test_vested_value_valuation_on_timeline_date(client: TestClient) -> None:
    """
        If valuation happens at the timeline date, we count equity
        value for this date with the new valuation price
    """
    data = {
        'option_grants': [
            {
                'quantity': 400,
                'start_date': '01-01-2018',
                'cliff_months': 2,
                'duration_months': 4
            }
        ],
        'company_valuations': [
            {
                'price': 10.0,
                'valuation_date': '15-12-2017'
            },
            {
                'price': 15.0,
                'valuation_date': '01-05-2018'
            },
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == [
        {
            'total_value': 0.0,
            'date': '01-01-2018'
        },
        {
            'total_value': 0.0,
            'date': '01-02-2018'
        },
        {
            'total_value': 2000.0,
            'date': '01-03-2018'
        },
        {
            'total_value': 3000.0,
            'date': '01-04-2018'
        },
        {
            'total_value': 6000.0,
            'date': '01-05-2018'
        },
    ]


def test_vested_value_falling_valuation(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 400,
                'start_date': '01-01-2018',
                'cliff_months': 2,
                'duration_months': 4
            }
        ],
        'company_valuations': [
            {
                'price': 10.0,
                'valuation_date': '15-12-2017'
            },
            {
                'price': 5.0,
                'valuation_date': '15-04-2018'
            }
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == [
        {
            'total_value': 0.0,
            'date': '01-01-2018'
        },
        {
            'total_value': 0.0,
            'date': '01-02-2018'
        },
        {
            'total_value': 2000.0,
            'date': '01-03-2018'
        },
        {
            'total_value': 3000.0,
            'date': '01-04-2018'
        },
        {
            'total_value': 2000.0,
            'date': '01-05-2018'
        },
    ]


def test_vested_value_valuations_outside_vesting_period(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 400,
                'start_date': '01-01-2018',
                'cliff_months': 2,
                'duration_months': 4
            }
        ],
        'company_valuations': [
            {
                'price': 50.0,
                'valuation_date': '15-12-2016'
            },
            {
                'price': 10.0,
                'valuation_date': '15-12-2017'
            },
            {
                'price': 50.0,
                'valuation_date': '02-05-2018'
            },
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == [
        {
            'total_value': 0.0,
            'date': '01-01-2018'
        },
        {
            'total_value': 0.0,
            'date': '01-02-2018'
        },
        {
            'total_value': 2000.0,
            'date': '01-03-2018'
        },
        {
            'total_value': 3000.0,
            'date': '01-04-2018'
        },
        {
            'total_value': 4000.0,
            'date': '01-05-2018'
        },
    ]


def test_vested_value_negative_valuation(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 400,
                'start_date': '01-01-2018',
                'cliff_months': 2,
                'duration_months': 4
            }
        ],
        'company_valuations': [
            {
                'price': -1.0,
                'valuation_date': '15-12-2017'
            },
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )
    assert response.status_code == 422

    response_data = response.json()
    assert response_data['detail'][0]['loc'] == ['body', 'company_valuations', 0, 'price']


def test_vested_value_no_valuations(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 800,
                'start_date': '01-01-2018',
                'cliff_months': 4,
                'duration_months': 8
            }
        ],
        'company_valuations': []
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )

    assert response.status_code == 422

    response_data = response.json()

    assert response_data['detail'][0]['loc'] == ['body', 'company_valuations']


def test_vested_value_future_grant(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 400,
                'start_date': '01-01-2040',
                'cliff_months': 2,
                'duration_months': 4
            },
        ],
        'company_valuations': [
            {
                'price': 10.0,
                'valuation_date': '15-12-2039'
            },
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == [
        {
            'total_value': 0.0,
            'date': '01-01-2040'
        },
        {
            'total_value': 0.0,
            'date': '01-02-2040'
        },
        {
            'total_value': 2000.0,
            'date': '01-03-2040'
        },
        {
            'total_value': 3000.0,
            'date': '01-04-2040'
        },
        {
            'total_value': 4000.0,
            'date': '01-05-2040'
        },
    ]


def test_vested_value_two_grants(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 400,
                'start_date': '01-01-2018',
                'cliff_months': 2,
                'duration_months': 4
            },
            {
                'quantity': 300,
                'start_date': '01-02-2018',
                'cliff_months': 2,
                'duration_months': 3
            }
        ],
        'company_valuations': [
            {
                'price': 10.0,
                'valuation_date': '15-12-2017'
            },
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == [
        {
            'total_value': 0.0,
            'date': '01-01-2018'
        },
        {
            'total_value': 0.0,
            'date': '01-02-2018'
        },
        {
            'total_value': 2000.0,
            'date': '01-03-2018'
        },
        {
            'total_value': 5000.0,
            'date': '01-04-2018'
        },
        {
            'total_value': 7000.0,
            'date': '01-05-2018'
        },
    ]


def test_vested_value_unsorted_grants(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 300,
                'start_date': '01-02-2018',
                'cliff_months': 2,
                'duration_months': 3
            },
            {
                'quantity': 400,
                'start_date': '01-01-2018',
                'cliff_months': 2,
                'duration_months': 4
            },
        ],
        'company_valuations': [
            {
                'price': 10.0,
                'valuation_date': '15-12-2017'
            },
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == [
        {
            'total_value': 0.0,
            'date': '01-01-2018'
        },
        {
            'total_value': 0.0,
            'date': '01-02-2018'
        },
        {
            'total_value': 2000.0,
            'date': '01-03-2018'
        },
        {
            'total_value': 5000.0,
            'date': '01-04-2018'
        },
        {
            'total_value': 7000.0,
            'date': '01-05-2018'
        },
    ]


def test_vested_value_not_intersected_grant_periods(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 400,
                'start_date': '01-01-2018',
                'cliff_months': 2,
                'duration_months': 4
            },
            {
                'quantity': 400,
                'start_date': '01-01-2019',
                'cliff_months': 2,
                'duration_months': 4
            },
        ],
        'company_valuations': [
            {
                'price': 10.0,
                'valuation_date': '15-12-2017'
            },
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == [
        {
            'total_value': 0.0,
            'date': '01-01-2018'
        },
        {
            'total_value': 0.0,
            'date': '01-02-2018'
        },
        {
            'total_value': 2000.0,
            'date': '01-03-2018'
        },
        {
            'total_value': 3000.0,
            'date': '01-04-2018'
        },
        {
            'total_value': 4000.0,
            'date': '01-05-2018'
        },
        *[
            {
                'total_value': 4000.0,
                'date': f'01-{i:02d}-2018'
            }
            for i in [6, 7, 8, 9, 10, 11, 12]
        ],
        {
            'total_value': 4000.0,
            'date': '01-01-2019'
        },
        {
            'total_value': 4000.0,
            'date': '01-02-2019'
        },
        {
            'total_value': 6000.0,
            'date': '01-03-2019'
        },
        {
            'total_value': 7000.0,
            'date': '01-04-2019'
        },
        {
            'total_value': 8000.0,
            'date': '01-05-2019'
        },
    ]


def test_vested_value_grant_starting_in_the_middle_of_a_month(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 400,
                'start_date': '17-01-2018',
                'cliff_months': 2,
                'duration_months': 4
            },
        ],
        'company_valuations': [
            {
                'price': 10.0,
                'valuation_date': '15-12-2017'
            },
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == [
        {
            'total_value': 0.0,
            'date': '17-01-2018'
        },
        {
            'total_value': 0.0,
            'date': '01-02-2018'
        },
        {
            'total_value': 0.0,
            'date': '01-03-2018'
        },
        {
            'total_value': 2000.0,
            'date': '01-04-2018'
        },
        {
            'total_value': 3000.0,
            'date': '01-05-2018'
        },
        {
            'total_value': 4000.0,
            'date': '17-05-2018'
        },
    ]


def test_vested_value_grant_starting_at_the_end_of_a_month(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 400,
                'start_date': '31-10-2018',
                'cliff_months': 2,
                'duration_months': 4
            },
        ],
        'company_valuations': [
            {
                'price': 10.0,
                'valuation_date': '15-12-2017'
            },
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == [
        {
            'total_value': 0.0,
            'date': '31-10-2018'
        },
        {
            'total_value': 0.0,
            'date': '01-11-2018'
        },
        {
            'total_value': 0.0,
            'date': '01-12-2018'
        },
        {
            'total_value': 2000.0,
            'date': '01-01-2019'
        },
        {
            'total_value': 3000.0,
            'date': '01-02-2019'
        },
        {
            'total_value': 4000.0,
            'date': '28-02-2019'
        },
    ]


def test_vested_value_no_cliff(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 800,
                'start_date': '01-01-2018',
                'cliff_months': 0,
                'duration_months': 4
            }
        ],
        'company_valuations': [
            {
                'price': 10.0,
                'valuation_date': '09-12-2017'
            }
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data == [
        {
            'total_value': 0.0,
            'date': '01-01-2018'
        },
        {
            'total_value': 2000.0,
            'date': '01-02-2018'
        },
        {
            'total_value': 4000.0,
            'date': '01-03-2018'
        },
        {
            'total_value': 6000.0,
            'date': '01-04-2018'
        },
        {
            'total_value': 8000.0,
            'date': '01-05-2018'
        },
    ]


def test_vested_value_cliff_equals_to_duration(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 800,
                'start_date': '01-01-2018',
                'cliff_months': 4,
                'duration_months': 4
            }
        ],
        'company_valuations': [
            {
                'price': 10.0,
                'valuation_date': '09-12-2017'
            }
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data == [
        {
            'total_value': 0.0,
            'date': '01-01-2018'
        },
        {
            'total_value': 0.0,
            'date': '01-02-2018'
        },
        {
            'total_value': 0.0,
            'date': '01-03-2018'
        },
        {
            'total_value': 0.0,
            'date': '01-04-2018'
        },
        {
            'total_value': 8000.0,
            'date': '01-05-2018'
        },
    ]


def test_vested_value_one_month_cliff(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 800,
                'start_date': '01-01-2018',
                'cliff_months': 1,
                'duration_months': 4
            }
        ],
        'company_valuations': [
            {
                'price': 10.0,
                'valuation_date': '09-12-2017'
            }
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data == [
        {
            'total_value': 0.0,
            'date': '01-01-2018'
        },
        {
            'total_value': 2000.0,
            'date': '01-02-2018'
        },
        {
            'total_value': 4000.0,
            'date': '01-03-2018'
        },
        {
            'total_value': 6000.0,
            'date': '01-04-2018'
        },
        {
            'total_value': 8000.0,
            'date': '01-05-2018'
        },
    ]


def test_vested_value_cliff_higher_than_duration(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 800,
                'start_date': '01-01-2018',
                'cliff_months': 5,
                'duration_months': 4
            }
        ],
        'company_valuations': [
            {
                'price': 10.0,
                'valuation_date': '09-12-2017'
            }
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )

    assert response.status_code == 422

    response_data = response.json()

    assert response_data['detail'][0]['loc'] == ['body', 'option_grants', 0, '__root__']


def test_vested_value_two_grants_two_valuations(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 40,
                'start_date': '01-01-2018',
                'cliff_months': 2,
                'duration_months': 4
            },
            {
                'quantity': 60,
                'start_date': '01-02-2018',
                'cliff_months': 2,
                'duration_months': 4
            }
        ],
        'company_valuations': [
            {
                'price': 10.0,
                'valuation_date': '15-12-2017'
            },
            {
                'price': 15.0,
                'valuation_date': '15-04-2018'
            },
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == [
        {
            # pre-cliff / NA
            'total_value': 0.0,
            'date': '01-01-2018'
        },
        {
            # pre-cliff / pre-cliff
            'total_value': 0.0,
            'date': '01-02-2018'
        },
        {
            # cliff / pre-cliff (2 * 10 + 0) * 10
            'total_value': 200.0,
            'date': '01-03-2018'
        },
        {
            # 3mo / cliff (3 * 10 + 2 * 15) * 10
            'total_value': 600.0,
            'date': '01-04-2018'
        },
        {
            # new price: 4mo / 3mo (4 * 10 + 3 * 15) * 15
            'total_value': 1275.0,
            'date': '01-05-2018'
        },
        {
            # new price: 4mo / 4mo (4 * 10 + 4 * 15) * 15
            'total_value': 1500.0,
            'date': '01-06-2018'
        },
    ]


def test_vested_value_two_grants_two_valuations_different_days(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 40,
                'start_date': '17-01-2018',
                'cliff_months': 2,
                'duration_months': 4
            },
            {
                'quantity': 60,
                'start_date': '01-02-2018',
                'cliff_months': 2,
                'duration_months': 4
            }
        ],
        'company_valuations': [
            {
                'price': 10.0,
                'valuation_date': '15-12-2017'
            },
            {
                'price': 15.0,
                'valuation_date': '15-04-2018'
            },
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == [
        {
            # pre-cliff / NA
            'total_value': 0.0,
            'date': '17-01-2018'
        },
        {
            # pre-cliff / pre-cliff
            'total_value': 0.0,
            'date': '01-02-2018'
        },
        {
            # pre-cliff  / pre-cliff
            'total_value': 0.0,
            'date': '01-03-2018'
        },
        {
            # cliff / cliff (2 * 10 + 2 * 15) * 10
            'total_value': 500.0,
            'date': '01-04-2018'
        },
        {
            # new price: 3mo / 3mo (3 * 10 + 3 * 15) * 15
            'total_value': 1125.0,
            'date': '01-05-2018'
        },
        {
            # new price: 4mo / 4mo (4 * 10 + 4 * 15) * 15
            'total_value': 1500.0,
            'date': '01-06-2018'
        },
    ]


def test_vested_value_no_grants(client: TestClient) -> None:
    data = {
        'option_grants': [],
        'company_valuations': [
            {
                'price': 10.0,
                'valuation_date': '09-12-2017'
            }
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )

    assert response.status_code == 422

    response_data = response.json()

    assert response_data['detail'][0]['loc'] == ['body', 'option_grants']


def test_vested_value_decimal_stock_price(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 10,
                'start_date': '01-01-2018',
                'cliff_months': 0,
                'duration_months': 2
            },
            {
                'quantity': 2,
                'start_date': '01-02-2018',
                'cliff_months': 0,
                'duration_months': 2
            },

        ],
        'company_valuations': [
            {
                'price': 77.77,
                'valuation_date': '15-12-2017'
            },
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == [
        {
            'total_value': 0.0,
            'date': '01-01-2018'
        },
        {
            'total_value': float(Decimal('77.77') * 5),
            'date': '01-02-2018'
        },
        {
            'total_value': float(Decimal('77.77') * (10 + 1)),
            'date': '01-03-2018'
        },
        {
            'total_value': float(Decimal('77.77') * (10 + 2)),
            'date': '01-04-2018'
        },
    ]


def test_vested_value_only_whole_vested_value_counted_in_vested_quantity(
    client: TestClient
) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 27,
                'start_date': '01-01-2018',
                'cliff_months': 0,
                'duration_months': 5
            },

        ],
        'company_valuations': [
            {
                'price': 1.0,
                'valuation_date': '15-12-2017'
            },
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == [
        {
            'total_value': 0.0,
            'date': '01-01-2018'
        },
        {
            # 5.4 -> 5
            'total_value': 5.0,
            'date': '01-02-2018'
        },
        {
            # 10.8 -> 10
            'total_value': 10.0,
            'date': '01-03-2018'
        },
        {
            # 16.2 -> 16
            'total_value': 16.0,
            'date': '01-04-2018'
        },
        {
            # 21.6 -> 21
            'total_value': 21.0,
            'date': '01-05-2018'
        },
        {
            'total_value': 27.0,
            'date': '01-06-2018'
        },
    ]


def test_vested_value_periodic_decimal_monthly_vested_quantity(client: TestClient) -> None:
    data = {
        'option_grants': [
            {
                'quantity': 1,
                'start_date': '01-01-2018',
                'cliff_months': 0,
                'duration_months': 3
            },

        ],
        'company_valuations': [
            {
                'price': 1.0,
                'valuation_date': '15-12-2017'
            },
        ]
    }

    response = client.post(
        f'{settings.API_V1_STR}/timelines/vested_value',
        json=data,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == [
        {
            'total_value': 0.0,
            'date': '01-01-2018'
        },
        {
            # 1/3 -> 0
            'total_value': 0.0,
            'date': '01-02-2018'
        },
        {
            # 2/3 -> 0
            'total_value': 0.0,
            'date': '01-03-2018'
        },
        {
            'total_value': 1.0,
            'date': '01-04-2018'
        },
    ]

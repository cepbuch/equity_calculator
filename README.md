# Equity Calculator API

API that calculates the value of the vested equity over time.

Launch instruction:

1. `git clone git@github.com:cepbuch/equity_calculator.git`
2. `cd equity_calculator/equity_calculator`
3. `docker compose up`
4. The documentation is available at http://127.0.0.1:8080/docs, and main API endpoint is http://127.0.0.1:8080/api/v1/timelines/vested_value

<details>
  <summary>Example</summary>
  
  ```bash
  curl -X POST 'http://127.0.0.1:8080/api/v1/timelines/vested_value' \
  -H 'Content-Type: application/json; charset=utf-8' \
  --data-binary @- << EOF
  {
      "option_grants": [
          {
              "quantity": 4800,
              "start_date": "01-01-2018",
              "cliff_months": 12,
              "duration_months": 48
          }
      ],
      "company_valuations": [
          {
              "price": 10.0,
              "valuation_date": "09-12-2017"
          }
      ]
  }
  EOF
  ```
  
</details>

OrderRenderBase = """{
  "name": "DF",
  "fields": {
    "items": [
      {
        "name": "Order",
        "fields": [
          {
            "attr": "order_id",
            "storage": [
              "order"
            ],
            "format": null,
            "before_value": null,
            "after_value": null
          }
        ],
        "markdown_name": "<b>",
        "markdown_value": null,
        "separator": " "
      },
      {
        "name": "Description",
        "fields": [
          {
            "attr": "boost_type",
            "storage": [
              "order", "info"
            ],
            "format": null,
            "before_value": null,
            "after_value": null
          },
          {
            "attr": "game",
            "storage": [
              "order"
            ],
            "format": null,
            "before_value": null,
            "after_value": null
          },
          {
            "attr": "category",
            "storage": [
              "order"
            ],
            "format": null,
            "before_value": null,
            "after_value": null
          },
          {
            "attr": "purchase",
            "storage": [
              "order"
            ],
            "format": null,
            "before_value": null,
            "after_value": null
          }
        ],
        "markdown_name": "<b>",
        "markdown_value": "<code>",
        "separator": " "
      },
      {
        "name": "Additional Info",
        "fields": [
          {
            "attr": "comment",
            "storage": [
              "order", "info"
            ],
            "format": null,
            "before_value": null,
            "after_value": null
          }
        ],
        "markdown_name": "<b>",
        "markdown_value": "<code>",
        "separator": " "
      }
    ]
  },
  "separator": "\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n",
  "separator_field": "\n"
}"""

OrderRenderEtaPrice = """{
  "name": "eta-price",
  "fields": {
    "items": [
      {
        "name": "ETA",
        "fields": [
          {
            "attr": "eta",
            "storage": [
              "order", "info"
            ],
            "format": null,
            "before_value": "string",
            "after_value": "string"
          }
        ],
        "markdown_name": "<b>",
        "markdown_value": "<code>",
        "separator": " "
      },
      {
        "name": "Price",
        "fields": [
          {
            "attr": "price_booster_rub",
            "storage": [
              "order"
            ],
            "format": ".2f",
            "before_value": null,
            "after_value": "р."
          },
          {
            "attr": "price_booster_dollar_fee",
            "storage": [
              "order"
            ],
            "format": ".2f",
            "before_value": "(",
            "after_value": "$)"
          }
        ],
        "markdown_name": "<b>",
        "markdown_value": "<code>",
        "separator": " "
      }
    ]
  },
  "separator": "\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n",
  "separator_field": "\n"
}"""

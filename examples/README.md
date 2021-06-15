# Overview

This repository contains Jupyter notebooks that show how to use [LUSID](https://www.finbourne.com/lusid-technology). The examples in this repository are in Python. but the underlying LUSID functionality can be implemented using any language which can call our standard REST APIs. The notebooks are divided into two categories:

* `features` - Notebooks showing specific LUSID features. For example, there is notebook showing you how to call holdings using a get holdings request. These notebooks are generally short and specific.
* `use-cases` - Notebooks showing sample business implementations or use-cases. These notebooks will generally combine various LUSID features to solve a business use-case. For example, there is notebook which uses the LUSID features of derived portfolios, quotes, and get holdings to back-test a trading strategy. These `use-case` notebooks are generally longer than the `features` ones.

## examples/entitlements
| filename | title | description | features |
| --- | --- | --- | --- |
| [Property value entitlements.ipynb](<entitlements/Property value entitlements.ipynb>) | Portfolio look-through in LUSID |  | entitlements, property values, transactions |

## examples/features/core-lusid
| filename | title | description | features |
| --- | --- | --- | --- |
| [Bi-temporal example.ipynb](<features/core-lusid/Bi-temporal example.ipynb>) | Bi-temporal Example | Demonstration of how the asAt date can be used to get data from different system dates. | bi-temporality, cocoon - identify_cash_items, holdings, transaction configuration, transactions |
| [Cancelling transactions in LUSID.ipynb](<features/core-lusid/Cancelling transactions in LUSID.ipynb>) | Cancelling transactions | Demonstration of how to use the CancelTransactions endpoint to cancel transactions in a LUSID portfolio. | cancel transactions, cocoon - seed_data, holdings, transactions |
| [Derived portfolios.ipynb](<features/core-lusid/Derived portfolios.ipynb>) | Derived portfolios |  | derived portfolios, holdings, transactions |
| [Generating an IBOR extract with LUSID's GetHoldings method.ipynb](<features/core-lusid/Generating an IBOR extract with LUSID's GetHoldings method.ipynb>) | Generating an IBOR extract |  | cocoon - seed_data, holdings |
| [Multi-Value Properties.ipynb](<features/core-lusid/Multi-Value Properties.ipynb>) | Time-variant Properties (e.g. coupon schedule) in LUSID  |  | coupon schedules, multi-valued properties, time-variant properties |
| [Output Transactions.ipynb](<features/core-lusid/Output Transactions.ipynb>) | Output Transactions | This notebook shows how LUSID uses synthetic transactions to fill in the gaps between user-instructed transactions and corporate actions. | adjust holdings, build transactions, corporate actions, instruments, output transactions, portfolios, stock split, sub-holding keys, transactions |
| [Paging and limiting LUSID's API calls.ipynb](<features/core-lusid/Paging and limiting LUSID's API calls.ipynb>) | Paging and limiting LUSID's API calls |  | paging |
| [Processing Corporate Actions as input transactions.ipynb](<features/core-lusid/Processing Corporate Actions as input transactions.ipynb>) | Processing Corporate Actions as input transactions | Demonstration of booking corporate action transactions using LUSID's standard input transactions | cocoon - seed_data, holdings, transaction configuration, transactions |
| [Processing Corporate Actions as native LUSID transitions.ipynb](<features/core-lusid/Processing Corporate Actions as native LUSID transitions.ipynb>) | Processing Corporate Actions using LUSID transitions | Demonstration of booking corporate actions using LUSID's transitions | cocoon - seed_data, corporate actions, holdings, transaction configuration, transactions |
| [Sub-holding Keys.ipynb](<features/core-lusid/Sub-holding Keys.ipynb>) | Sub-Holding Keys | Demonstration of how to set up and use sub-holding keys | cocoon - seed_data, holdings, properties, prorated, sub-holding keys |
| [TimeVariant Properties.ipynb](<features/core-lusid/TimeVariant Properties.ipynb>) | Time-variant Properties (e.g. coupon schedule) in LUSID  |  | coupon schedules, multi-valued properties, time-variant properties |

## examples/features/core-lusid/relations
| filename | title | description | features |
| --- | --- | --- | --- |
| [Relations.ipynb](<features/core-lusid/relations/Relations.ipynb>) | Relations |  | relations |

## examples/use-cases/abor
| filename | title | description | features |
| --- | --- | --- | --- |
| [Generate P&amp;L with different accounting methods (FIFO and LIFO).ipynb](<use-cases/abor/Generate P&amp;L with different accounting methods (FIFO and LIFO).ipynb>) | Accounting methods | Generating P&amp;L with different accounting methods (FIFO and LIFO) | accounting methods, cocoon, derived portfolios, transaction configuration |

## examples/use-cases/audit-trail
| filename | title | description | features |
| --- | --- | --- | --- |
| [Identifying Downstream Consumers affected by Backdated Corrections on a Locked Reporting Window.ipynb](<use-cases/audit-trail/Identifying Downstream Consumers affected by Backdated Corrections on a Locked Reporting Window.ipynb>) | Identifying backdated corrections | Demonstration of how to identify backdated corrections and their impact | build transaction, cocoon - seed_data, insights, portfolio changes |

## examples/use-cases/cash-management
| filename | title | description | features |
| --- | --- | --- | --- |
| [Accruals.ipynb](<use-cases/cash-management/Accruals.ipynb>) | Accruals | Demonstration of how to model accruals in LUSID | cocoon, holdings, transaction configuration |
| [Booking subscriptions and redemptions.ipynb](<use-cases/cash-management/Booking subscriptions and redemptions.ipynb>) | Booking subscriptions and redemptions | Demonstration of how to model subscriptions and redemptions in LUSID | cocoon - seed_data, holdings, transaction configuration |
| [Manual journal entries to correct cash balances.ipynb](<use-cases/cash-management/Manual journal entries to correct cash balances.ipynb>) | Correcting cash balances with manual journal entries | Demonstration of how to model manual journal entries in LUSID | cancel transactions, cocoon, holdings, reconciliations, transaction configuration |

## examples/use-cases/change-management
| filename | title | description | features |
| --- | --- | --- | --- |
| [Business Agility - migration between investment systems.ipynb](<use-cases/change-management/Business Agility - migration between investment systems.ipynb>) | Business agility | Demonstration of how to migrate your data from one system to another. | holdings, instruments, properties, reconciliations, set holdings, transaction configuration, transactions |
| [Safely and efficiently test changes to your system.ipynb](<use-cases/change-management/Safely and efficiently test changes to your system.ipynb>) | Testing system changes | Demonstration of how to safely test changes to your data in a production environment | derived portfolios, instrument definitions, instruments, set holdings, transactions |
| [Set up a sandbox trading environment.ipynb](<use-cases/change-management/Set up a sandbox trading environment.ipynb>) | Sandbox trading environment |  | aggregation, instruments, properties, quotes, reference portfolios, set holdings, transactions |

## examples/use-cases/ibor
| filename | title | description | features |
| --- | --- | --- | --- |
| [Generating Corporate actions natively in LUSID.ipynb](<use-cases/ibor/Generating Corporate actions natively in LUSID.ipynb>) | Corporate Actions in LUSID |  | corporate actions, derived portfolios, holdings, transactions |
| [Generating holdings with the movements engine in LUSID.ipynb](<use-cases/ibor/Generating holdings with the movements engine in LUSID.ipynb>) | Generating holdings | Generating holdings with the movements engine | cocoon, instruments, transaction configuration, transactions |
| [Get a consolidated view of your data from multiple systems.ipynb](<use-cases/ibor/Get a consolidated view of your data from multiple systems.ipynb>) | Consolidating multiple systems | Demonstration of how to migrate funds from multiple source systems into LUSID | aggregation, holdings, instruments, properties, quotes, reconciliations, transaction configuration |
| [How do I create holdings in LUSID.ipynb](<use-cases/ibor/How do I create holdings in LUSID.ipynb>) | Creating holdings in LUSID |  | properties, transaction configuration, transactions |
| [IBOR User Journey.ipynb](<use-cases/ibor/IBOR User Journey.ipynb>) | IBOR User Journey | A day in the life of an IBOR using LUSID | aggregation, aggregation, cocoon, corporate actions, instruments, quotes, results store, sub-holding keys, transaction configuration, valuation reconciliation |
| [Load Transactions from an External System.ipynb](<use-cases/ibor/Load Transactions from an External System.ipynb>) | Loading transactions from an external system | Demonstration of loading a transaction XML file from another &quot;External System&quot; into LUSID. | cocoon, holdings, transactions |
| [Loading data with the Lusid-Python-Tools (LPT) package.ipynb](<use-cases/ibor/Loading data with the Lusid-Python-Tools (LPT) package.ipynb>) | Loading data with LUSID Python Tools |  | cocoon, instruments, portfolios, transactions |
| [Maintain a fund in multiple currencies and share classes.ipynb](<use-cases/ibor/Maintain a fund in multiple currencies and share classes.ipynb>) | Modelling share classes in LUSID |  | adjust holdings, aggregation, holdings, instrument definitions, quotes, transactions |
| [Maintaining an instrument master in LUSID.ipynb](<use-cases/ibor/Maintaining an instrument master in LUSID.ipynb>) | Maintaining an instrument master |  | instruments, properties, search |
| [Perform a reconciliation.ipynb](<use-cases/ibor/Perform a reconciliation.ipynb>) | Reconciliations | Demonstration of how to use LUSID to find discrepancies between versions of a portfolio | adjust holdings, instruments, portfolio groups, properties, reconciliations, set holdings, transactions |
| [Portfolio types and portfolio groups in LUSID.ipynb](<use-cases/ibor/Portfolio types and portfolio groups in LUSID.ipynb>) | Portfolios and Portfolio Groups |  | commands, corporate actions, portfolio groups, portfolios, transactions |
| [Running a Global Fund.ipynb](<use-cases/ibor/Running a Global Fund.ipynb>) | Running a global fund | Demonstration of using LUSID to run funds fed from multiple source systems across multiple regions | aggregation, cocoon, cut labels, instruments, quotes, recipes, transaction configuration, transactions |
| [Using cut-labels to manage your business across different time-zones.ipynb](<use-cases/ibor/Using cut-labels to manage your business across different time-zones.ipynb>) | Cut Labels |  | cut labels, holdings, instruments, transactions |

## examples/use-cases/orders-management
| filename | title | description | features |
| --- | --- | --- | --- |
| [Combining FO and MO.ipynb](<use-cases/orders-management/Combining FO and MO.ipynb>) | Combining Front Office and Middle Office | Demonstration of how to give front office users an view of intraday trading activity on top of their middle office IBOR. | cocoon, derived portfolios, instruments, orders, properties, sub-holdings keys, transactions |

## examples/use-cases/post-trade-processing
| filename | title | description | features |
| --- | --- | --- | --- |
| [Managing a transaction lifecycle using LUSID's properties.ipynb](<use-cases/post-trade-processing/Managing a transaction lifecycle using LUSID's properties.ipynb>) | Managing the transaction lifecycle on LUSID | Demonstration of how to use properties to manage the transaction lifecycle | cocoon, data types, instruments, properties, transactions |

## examples/use-cases/private-assets
| filename | title | description | features |
| --- | --- | --- | --- |
| [Managing cashflows - capital calls and income distributions.ipynb](<use-cases/private-assets/Managing cashflows - capital calls and income distributions.ipynb>) | Running a Fund with Investors | Demonstration of how to manage a fund's subscriptions and capital calls with investors in LUSID | holdings, instruments, properties, transaction configuration, transactions |
| [Supporting a multi-asset class book of business.ipynb](<use-cases/private-assets/Supporting a multi-asset class book of business.ipynb>) | Bespoke asset classes | Demonstration of how to create your own custom instrument inside LUSID, create a transaction against it and value it. | aggregation, instruments, properties, quotes, transactions |

## examples/use-cases/risk-and-performance
| filename | title | description | features |
| --- | --- | --- | --- |
| [Backtesting with LUSID derived portfolios.ipynb](<use-cases/risk-and-performance/Backtesting with LUSID derived portfolios.ipynb>) | Backtesting with derived portfolios |  | aggregation, cocoon, derived portfolios, holdings, instruments, quotes |
| [Calculating P&amp;L on strategy.ipynb](<use-cases/risk-and-performance/Calculating P&amp;L on strategy.ipynb>) | Calculating P&amp;L on strategies | Demonstration of how to use sub-holding keys and output transactions to track P&amp;L on different strategies. | cocoon - seed_data, derived portfolios, output transactions, properties, sub-holding keys, transactions |
| [Loading and calculating returns.ipynb](<use-cases/risk-and-performance/Loading and calculating returns.ipynb>) | Loading and caculating returns | Demonstration of how to load and calculate returns in LUSID. | Returns |
| [Manage your investment strategies.ipynb](<use-cases/risk-and-performance/Manage your investment strategies.ipynb>) | Managing investment strategies | Demonstration of how to compare how strategies are performing across all of our client's holdings, rather than just looking at a single portfolio in isolation. | aggregation, data types, instruments, portfolio groups, properties, set holdings, transactions |
| [Rebalancing with a model portfolio.ipynb](<use-cases/risk-and-performance/Rebalancing with a model portfolio.ipynb>) | Rebalancing with a model portfolio  | This notebook shows how to you can automatically generate transactions to rebalance a transaction portfolio with a model portfolio | reference portfolios, transactions portfolios |
| [Returns on composite portfolios.ipynb](<use-cases/risk-and-performance/Returns on composite portfolios.ipynb>) | Loading and caculating returns | Demonstration of how to load and calculate returns on composite portfolios in LUSID | Composite portfolios, Returns |
| [Setting up a blended benchmark with floating weights.ipynb](<use-cases/risk-and-performance/Setting up a blended benchmark with floating weights.ipynb>) | Setting up a blended benchmark | Demonstration of how to load a blended benchmark. 
We also show how floating weights with a periodic reset. | Floating weights, Reference portfolios, Securitised portfolios, Weights |
| [Track trading commissions in your portfolio.ipynb](<use-cases/risk-and-performance/Track trading commissions in your portfolio.ipynb>) | Track trading costs and commissions in your portfolio |  | cocoon, instruments, portfolio groups, properties, sub-holding keys, transaction configuration, transactions |

## examples/use-cases/valuation
| filename | title | description | features |
| --- | --- | --- | --- |
| [Bond Pricing And Accrued Interest Calculation.ipynb](<use-cases/valuation/Bond Pricing And Accrued Interest Calculation.ipynb>) | Bond Pricing And Accrued Interest Calculation | Demonstrates pricing a bond and calculating it's accrued interest based on a user defined Bond Instrument. | aggregation, instruments, market data store, quotes, results store |
| [Look-through valuation.ipynb](<use-cases/valuation/Look-through valuation.ipynb>) | Portfolio look-through in LUSID |  | holdings, look through, portfolios, securitised portfolios, valuations |
| [Simple Valuation.ipynb](<use-cases/valuation/Simple Valuation.ipynb>) | Simple valuation with default recipes | This notebook shows how to value a portfolio using defatul recipes, for an out of the box look at positions and valuations | manifests, recipes, transactions, valuation |
| [Valuations with recipes.ipynb](<use-cases/valuation/Valuations with recipes.ipynb>) | Valuation with recipes | This notebook shows how to value a portfolio using recipes with different pricing sources | manifests, recipes, transactions, valuation |

## examples/use-cases/wealth-management
| filename | title | description | features |
| --- | --- | --- | --- |
| [Households.ipynb](<use-cases/wealth-management/Households.ipynb>) | Households | Demonstration of how to manage the holdings for an investor based on each Mandate &amp; Household they are associated with. | aggregation, instruments, portfolio groups, portfolios, properties, quotes, set holdings |


| :warning: This file is generated, any direct edits will be lost. For instructions on how to generate the file, see [docgen/README](../docgen/). |
| --- |


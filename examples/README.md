# LUSID Jupyter notebooks

This repository contains Jupyter notebooks that show how to use [LUSID](https://www.finbourne.com/lusid-technology). The examples in this repository are in Python. but the underlying LUSID functionality can be implemented using any language that has a HTTP client library. The notebooks are divided into two categories:

* `features` - Notebooks showing specific LUSID features. These notebooks are short and specific.
* `use-cases` - Notebooks showing sample business implementations or use-cases. These notebooks will combine various LUSID features to solve a business use-case. The `use-case` notebooks are generally longer than the `features` ones.

## examples/entitlements
| filename | title | description | features |
| --- | --- | --- | --- |
| [Portfolio Entitlements.ipynb](<entitlements/Portfolio%20Entitlements.ipynb>) | Portfolio Entitlements | Demonstrates how to create policies/access control to various date items. | entitlements |
| [Property value entitlements.ipynb](<entitlements/Property%20value%20entitlements.ipynb>) | Portfolio look-through in LUSID | Demonstrates the use of policies to grant access to property values in LUSID. | entitlements, property values, transactions |

## examples/features/core-lusid
| filename | title | description | features |
| --- | --- | --- | --- |
| [Bi-temporal example.ipynb](<features/core-lusid/Bi-temporal%20example.ipynb>) | Bi-temporal Example | Demonstration of how the asAt date can be used to get data from different system dates. | bi-temporality, cocoon - identify_cash_items, holdings, transaction configuration, transactions |
| [Cancelling transactions in LUSID.ipynb](<features/core-lusid/Cancelling%20transactions%20in%20LUSID.ipynb>) | Cancelling transactions | Demonstration of how to use the CancelTransactions endpoint to cancel transactions in a LUSID portfolio. | cancel transactions, cocoon - seed_data, holdings, transactions |
| [Derived portfolios.ipynb](<features/core-lusid/Derived%20portfolios.ipynb>) | Derived portfolios | Shows how to use derived portfolios, a type of portfolio that inherits the contents from a parent portfolio. | derived portfolios, holdings, transactions |
| [Generating an IBOR extract with LUSID's GetHoldings method.ipynb](<features/core-lusid/Generating%20an%20IBOR%20extract%20with%20LUSID%27s%20GetHoldings%20method.ipynb>) | Generating an IBOR extract | Demonstrates how to use the GetHoldings API to generate IBOR extracts. | cocoon - seed_data, holdings |
| [Multi-Value Properties.ipynb](<features/core-lusid/Multi-Value%20Properties.ipynb>) | Time-variant Properties (e.g. coupon schedule) in LUSID  | Illustrates the use of multi-value properties. | coupon schedules, multi-valued properties, time-variant properties |
| [Output Transactions.ipynb](<features/core-lusid/Output%20Transactions.ipynb>) | Output Transactions | This notebook shows how LUSID uses synthetic transactions to fill in the gaps between user-instructed transactions and corporate actions. | adjust holdings, build transactions, corporate actions, instruments, output transactions, portfolios, stock split, sub-holding keys, transactions |
| [Paging and limiting LUSID's API calls.ipynb](<features/core-lusid/Paging%20and%20limiting%20LUSID%27s%20API%20calls.ipynb>) | Paging and limiting LUSID's API calls | Shows how to slice up large requests to LUSID into smaller requests using the limit and page parameters. | paging |
| [Processing Corporate Actions as input transactions.ipynb](<features/core-lusid/Processing%20Corporate%20Actions%20as%20input%20transactions.ipynb>) | Processing Corporate Actions as input transactions | Demonstration of booking corporate action transactions using LUSID's standard input transactions | cocoon - seed_data, holdings, transaction configuration, transactions |
| [Processing Corporate Actions as native LUSID transitions.ipynb](<features/core-lusid/Processing%20Corporate%20Actions%20as%20native%20LUSID%20transitions.ipynb>) | Processing Corporate Actions using LUSID transitions | Demonstration of booking corporate actions using LUSID's transitions | cocoon - seed_data, corporate actions, holdings, transaction configuration, transactions |
| [Sub-holding Keys.ipynb](<features/core-lusid/Sub-holding%20Keys.ipynb>) | Sub-Holding Keys | Demonstration of how to set up and use sub-holding keys | cocoon - seed_data, holdings, properties, prorated, sub-holding keys |
| [TimeVariant Properties.ipynb](<features/core-lusid/TimeVariant%20Properties.ipynb>) | Time-variant Properties (e.g. coupon schedule) in LUSID  | Illustrates the use of time-variant properties, a type of property that depend on different effective dates. | coupon schedules, multi-valued properties, time-variant properties |

## examples/features/core-lusid/relations
| filename | title | description | features |
| --- | --- | --- | --- |
| [Relations.ipynb](<features/core-lusid/relations/Relations.ipynb>) | Relations | Demonstrates how to create relationships between different portfolios. | relations |

## examples/features/data-feeds
| filename | title | description | features |
| --- | --- | --- | --- |
| [Using TraderMade FX spot price data in LUSID.ipynb](<features/data-feeds/Using%20TraderMade%20FX%20spot%20price%20data%20in%20LUSID.ipynb>) | Using TraderMade FX spot price data in LUSID | This notebook shows you how to access TraderMade spot FX data in LUSID | quotes |

## examples/modules
| filename | title | description | features |
| --- | --- | --- | --- |
| [Valuation.ipynb](<modules/Valuation.ipynb>) | Valuation | Demonstrates how to value a portfolio using a custom recipe. | valuation |
| [bitemporal-backtrade.ipynb](<modules/bitemporal-backtrade.ipynb>) | Bi-temporal backtrade | Demonstrates how to add a missing trade and then get back transactions using the AsAt date. | bi-temporality |
| [cashladder.ipynb](<modules/cashladder.ipynb>) | Cash ladder | Demonstration of how to compute a cash ladder across different currencies for a portfolio. | cash |

## examples/use-cases/abor
| filename | title | description | features |
| --- | --- | --- | --- |
| [Generate P&amp;L with different accounting methods (FIFO and LIFO).ipynb](<use-cases/abor/Generate%20P%26L%20with%20different%20accounting%20methods%20%28FIFO%20and%20LIFO%29.ipynb>) | Accounting methods | Generating P&L with different accounting methods (FIFO and LIFO) | accounting methods, cocoon, derived portfolios, transaction configuration |

## examples/use-cases/audit-trail
| filename | title | description | features |
| --- | --- | --- | --- |
| [Identifying Downstream Consumers affected by Backdated Corrections on a Locked Reporting Window.ipynb](<use-cases/audit-trail/Identifying%20Downstream%20Consumers%20affected%20by%20Backdated%20Corrections%20on%20a%20Locked%20Reporting%20Window.ipynb>) | Identifying backdated corrections | Demonstration of how to identify backdated corrections and their impact | build transaction, cocoon - seed_data, insights, portfolio changes |

## examples/use-cases/cash-management
| filename | title | description | features |
| --- | --- | --- | --- |
| [Accruals.ipynb](<use-cases/cash-management/Accruals.ipynb>) | Accruals | Demonstration of how to model accruals in LUSID | cocoon, holdings, transaction configuration |
| [Booking subscriptions and redemptions.ipynb](<use-cases/cash-management/Booking%20subscriptions%20and%20redemptions.ipynb>) | Booking subscriptions and redemptions | Demonstration of how to model subscriptions and redemptions in LUSID | cocoon - seed_data, holdings, transaction configuration |
| [Cash ladder.ipynb](<use-cases/cash-management/Cash%20ladder.ipynb>) | Cash ladder | Demonstration of how to compute a cash ladder for a portfolio. | cash |
| [Manual journal entries to correct cash balances.ipynb](<use-cases/cash-management/Manual%20journal%20entries%20to%20correct%20cash%20balances.ipynb>) | Correcting cash balances with manual journal entries | Demonstration of how to model manual journal entries in LUSID | cancel transactions, cocoon, holdings, reconciliations, transaction configuration |

## examples/use-cases/change-management
| filename | title | description | features |
| --- | --- | --- | --- |
| [Business Agility - migration between investment systems.ipynb](<use-cases/change-management/Business%20Agility%20-%20migration%20between%20investment%20systems.ipynb>) | Business agility | Demonstration of how to migrate your data from one system to another. | holdings, instruments, properties, reconciliations, set holdings, transaction configuration, transactions |
| [Safely and efficiently test changes to your system.ipynb](<use-cases/change-management/Safely%20and%20efficiently%20test%20changes%20to%20your%20system.ipynb>) | Testing system changes | Demonstration of how to safely test changes to your data in a production environment | derived portfolios, instrument definitions, instruments, set holdings, transactions |
| [Set up a sandbox trading environment.ipynb](<use-cases/change-management/Set%20up%20a%20sandbox%20trading%20environment.ipynb>) | Sandbox trading environment | Learn how to setup a virtual trading environment in LUSID. | aggregation, instruments, properties, quotes, reference portfolios, set holdings, transactions |

## examples/use-cases/ibor
| filename | title | description | features |
| --- | --- | --- | --- |
| [Generating Corporate actions natively in LUSID.ipynb](<use-cases/ibor/Generating%20Corporate%20actions%20natively%20in%20LUSID.ipynb>) | Corporate Actions in LUSID | Demonstrates how to create and apply a corporate action to a portfolio. | corporate actions, derived portfolios, holdings, transactions |
| [Generating holdings with the movements engine in LUSID.ipynb](<use-cases/ibor/Generating%20holdings%20with%20the%20movements%20engine%20in%20LUSID.ipynb>) | Generating holdings | Generating holdings with the movements engine | cocoon, instruments, transaction configuration, transactions |
| [Get a consolidated view of your data from multiple systems.ipynb](<use-cases/ibor/Get%20a%20consolidated%20view%20of%20your%20data%20from%20multiple%20systems.ipynb>) | Consolidating multiple systems | Demonstration of how to migrate funds from multiple source systems into LUSID | aggregation, holdings, instruments, properties, quotes, reconciliations, transaction configuration |
| [How do I create holdings in LUSID.ipynb](<use-cases/ibor/How%20do%20I%20create%20holdings%20in%20LUSID.ipynb>) | Creating holdings in LUSID | Demonstrates how to load transactions based on custom transaction types and then compute the subsequent holdings. | properties, transaction configuration, transactions |
| [IBOR User Journey.ipynb](<use-cases/ibor/IBOR%20User%20Journey.ipynb>) | IBOR User Journey | A day in the life of an IBOR using LUSID | aggregation, aggregation, cocoon, corporate actions, instruments, quotes, results store, sub-holding keys, transaction configuration, valuation reconciliation |
| [Load Transactions from an External System.ipynb](<use-cases/ibor/Load%20Transactions%20from%20an%20External%20System.ipynb>) | Loading transactions from an external system | Demonstration of loading a transaction XML file from another "External System" into LUSID. | cocoon, holdings, transactions |
| [Loading data with the Lusid-Python-Tools (LPT) package.ipynb](<use-cases/ibor/Loading%20data%20with%20the%20Lusid-Python-Tools%20%28LPT%29%20package.ipynb>) | Loading data with LUSID Python Tools | Demonstrates how to load portfolios, instruments, holdings, and transactions. | cocoon, instruments, portfolios, transactions |
| [Maintain a fund in multiple currencies and share classes.ipynb](<use-cases/ibor/Maintain%20a%20fund%20in%20multiple%20currencies%20and%20share%20classes.ipynb>) | Modelling share classes in LUSID | This notebook shows how to model a fund that operates in different currencies and share classes. | adjust holdings, aggregation, holdings, instrument definitions, quotes, transactions |
| [Maintaining an instrument master in LUSID.ipynb](<use-cases/ibor/Maintaining%20an%20instrument%20master%20in%20LUSID.ipynb>) | Maintaining an instrument master | Demonstrates how to import, update, retrieve, and delete instruments. | instruments, properties, search |
| [Perform a reconciliation.ipynb](<use-cases/ibor/Perform%20a%20reconciliation.ipynb>) | Reconciliations | Demonstration of how to use LUSID to find discrepancies between versions of a portfolio | adjust holdings, instruments, portfolio groups, properties, reconciliations, set holdings, transactions |
| [Portfolio types and portfolio groups in LUSID.ipynb](<use-cases/ibor/Portfolio%20types%20and%20portfolio%20groups%20in%20LUSID.ipynb>) | Portfolios and Portfolio Groups | Demonstrates how to do various operations with portfolios and portfolio groups. | commands, corporate actions, portfolio groups, portfolios, transactions |
| [Running a Global Fund.ipynb](<use-cases/ibor/Running%20a%20Global%20Fund.ipynb>) | Running a global fund | Demonstration of using LUSID to run funds fed from multiple source systems across multiple regions | aggregation, cocoon, cut labels, instruments, quotes, recipes, transaction configuration, transactions |
| [Using cut-labels to manage your business across different time-zones.ipynb](<use-cases/ibor/Using%20cut-labels%20to%20manage%20your%20business%20across%20different%20time-zones.ipynb>) | Cut Labels | Demonstrates how to use cut labels to simplify timestamps and streamline usage of LUSID when used across multiple timezones. | cut labels, holdings, instruments, transactions |

## examples/use-cases/models-and-indices
| filename | title | description | features |
| --- | --- | --- | --- |
| [Rebalancing with a model portfolio.ipynb](<use-cases/models-and-indices/Rebalancing%20with%20a%20model%20portfolio.ipynb>) | Rebalancing with a model portfolio  | This notebook shows how to you can automatically generate transactions to rebalance a transaction portfolio with a model portfolio | reference portfolios, transactions portfolios |
| [Setting up a blended benchmark with floating weights.ipynb](<use-cases/models-and-indices/Setting%20up%20a%20blended%20benchmark%20with%20floating%20weights.ipynb>) | Setting up a blended benchmark | Demonstration of how to load a blended benchmark. <br>We also show how floating weights with a periodic reset. | Floating weights, Reference portfolios, Securitised portfolios, Weights |

## examples/use-cases/orders-management
| filename | title | description | features |
| --- | --- | --- | --- |
| [Combining FO and MO.ipynb](<use-cases/orders-management/Combining%20FO%20and%20MO.ipynb>) | Combining Front Office and Middle Office | Demonstration of how to give front office users an view of intraday trading activity on top of their middle office IBOR. | cocoon, derived portfolios, instruments, orders, properties, sub-holdings keys, transactions |

## examples/use-cases/post-trade-processing
| filename | title | description | features |
| --- | --- | --- | --- |
| [Managing a transaction lifecycle using LUSID's properties.ipynb](<use-cases/post-trade-processing/Managing%20a%20transaction%20lifecycle%20using%20LUSID%27s%20properties.ipynb>) | Managing the transaction lifecycle on LUSID | Demonstration of how to use properties to manage the transaction lifecycle | cocoon, data types, instruments, properties, transactions |

## examples/use-cases/private-assets
| filename | title | description | features |
| --- | --- | --- | --- |
| [Managing cashflows - capital calls and income distributions.ipynb](<use-cases/private-assets/Managing%20cashflows%20-%20capital%20calls%20and%20income%20distributions.ipynb>) | Running a Fund with Investors | Demonstration of how to manage a fund's subscriptions and capital calls with investors in LUSID | holdings, instruments, properties, transaction configuration, transactions |
| [Supporting a multi-asset class book of business.ipynb](<use-cases/private-assets/Supporting%20a%20multi-asset%20class%20book%20of%20business.ipynb>) | Bespoke asset classes | Demonstration of how to create your own custom instrument inside LUSID, create a transaction against it and value it. | aggregation, instruments, properties, quotes, transactions |

## examples/use-cases/risk-and-performance
| filename | title | description | features |
| --- | --- | --- | --- |
| [Backtesting with LUSID derived portfolios.ipynb](<use-cases/risk-and-performance/Backtesting%20with%20LUSID%20derived%20portfolios.ipynb>) | Backtesting with derived portfolios | Shows how to use a derived portfolio to test different trading strategies. | aggregation, cocoon, derived portfolios, holdings, instruments, quotes |
| [Calculating P&amp;L on strategy.ipynb](<use-cases/risk-and-performance/Calculating%20P%26L%20on%20strategy.ipynb>) | Calculating P&amp;L on strategies | Demonstration of how to use sub-holding keys and output transactions to track P&L on different strategies. | cocoon - seed_data, derived portfolios, output transactions, properties, sub-holding keys, transactions |
| [Loading and calculating returns.ipynb](<use-cases/risk-and-performance/Loading%20and%20calculating%20returns.ipynb>) | Loading and caculating returns | Demonstration of how to load and calculate returns in LUSID. | Returns |
| [Manage your investment strategies.ipynb](<use-cases/risk-and-performance/Manage%20your%20investment%20strategies.ipynb>) | Managing investment strategies | Demonstration of how to compare how strategies are performing across all of our client's holdings, rather than just looking at a single portfolio in isolation. | aggregation, data types, instruments, portfolio groups, properties, set holdings, transactions |
| [Returns on composite portfolios.ipynb](<use-cases/risk-and-performance/Returns%20on%20composite%20portfolios.ipynb>) | Loading and caculating returns | Demonstration of how to load and calculate returns on composite portfolios in LUSID | Composite portfolios, Returns |
| [Track trading commissions in your portfolio.ipynb](<use-cases/risk-and-performance/Track%20trading%20commissions%20in%20your%20portfolio.ipynb>) | Track trading costs and commissions in your portfolio | Demonstrates how to track commissions and fees separately from trade costs. | cocoon, instruments, portfolio groups, properties, sub-holding keys, transaction configuration, transactions |

## examples/use-cases/valuation
| filename | title | description | features |
| --- | --- | --- | --- |
| [Bond Pricing And Accrued Interest Calculation.ipynb](<use-cases/valuation/Bond%20Pricing%20And%20Accrued%20Interest%20Calculation.ipynb>) | Bond Pricing And Accrued Interest Calculation | Demonstrates pricing a bond and calculating it's accrued interest based on a user defined Bond Instrument. | aggregation, instruments, market data store, quotes, results store |
| [Futures Valuation with Differing Cost Basis Treatments (Synthetic Cash Method).ipynb](<use-cases/valuation/Futures%20Valuation%20with%20Differing%20Cost%20Basis%20Treatments%20%28Synthetic%20Cash%20Method%29.ipynb>) | Futures Valuation Workflow |  | futures, recipes, transaction types, valuations |
| [Futures Valuation with Differing Cost Basis Treatments.ipynb](<use-cases/valuation/Futures%20Valuation%20with%20Differing%20Cost%20Basis%20Treatments.ipynb>) | Futures Valuation Workflow |  | futures, recipes, transaction types, valuations |
| [Look-through valuation.ipynb](<use-cases/valuation/Look-through%20valuation.ipynb>) | Portfolio look-through in LUSID | Shows how to compute the value of a child portfolio's holding as though they were directly held by the parent portfolio. | holdings, look through, portfolios, securitised portfolios, valuations |
| [Simple Valuation.ipynb](<use-cases/valuation/Simple%20Valuation.ipynb>) | Simple valuation with default recipes | This notebook shows how to value a portfolio using defatul recipes, for an out of the box look at positions and valuations | manifests, recipes, transactions, valuation |
| [Valuations with recipes.ipynb](<use-cases/valuation/Valuations%20with%20recipes.ipynb>) | Valuation with recipes | This notebook shows how to value a portfolio using recipes with different pricing sources | manifests, recipes, transactions, valuation |

## examples/use-cases/wealth-management
| filename | title | description | features |
| --- | --- | --- | --- |
| [Households.ipynb](<use-cases/wealth-management/Households.ipynb>) | Households | Demonstration of how to manage the holdings for an investor based on each Mandate & Household they are associated with. | aggregation, instruments, portfolio groups, portfolios, properties, quotes, set holdings |


| :warning: This file is generated, any direct edits will be lost. For instructions on how to generate the file, see [docgen/README](../docgen/). |
| --- |


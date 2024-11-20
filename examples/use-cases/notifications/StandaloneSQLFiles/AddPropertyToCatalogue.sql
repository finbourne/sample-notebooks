@keysToCatalog = values
('Order/FinbourneUniversity/ExpPct', 'ExpPct', False, 'A property representing the Exposure Percentage of an order');

@config = select column1 as [Key], column2 as Name, column3 as IsMain, column4 as Description from @keysToCatalog;

select * from Sys.Admin.Lusid.Provider.Configure
where Provider = 'Lusid.PortfolioOrder'
and Configuration = @config
;
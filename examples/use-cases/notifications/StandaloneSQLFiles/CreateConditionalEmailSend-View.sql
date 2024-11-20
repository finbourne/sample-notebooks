@x =
use Sys.Admin.SetupView
--provider=Views.ConditionalEmailNotification
--parameters
EmailBody,Text,This is an email,true
OrderCode,Text,NotificationTestOrder1,true
OrderScope,Text,FinbourneUniversity,true
----

@@sep = select '--' || '--' as x;

@mapping_table = use Drive.Csv
--file=/TrainingFiles/MappingTable.csv
enduse;

@users = select
    EmailAddress,
    UserId,
    FirstName,
    LastName
from Sys.User.Role;

@raw_event_data = select
    PortfolioScope,
    PortfolioCode,
    OrderScope,
    OrderCode,
    Quantity,
    Side,
    Type,
    LimitPrice,
    UserIdModified,
    ClientInternal,
    Isin,
    ExpPct
from Lusid.PortfolioOrder
where OrderCode == #PARAMETERVALUE(OrderCode) and OrderScope == #PARAMETERVALUE(OrderScope)
;

@event_data = select
    *
from @raw_event_data r_e_d
inner join @users u on u.UserId = r_e_d.UserIdModified
;

@@portfolio = select PortfolioCode from @raw_event_data;
@@email = select Email from @mapping_table where Portfolio == @@portfolio;
@@name = select Name from @mapping_table where Portfolio == @@portfolio;

@@email_to = select '--addressTo="[' || @@name || '](' || @@email || ')"';

@@email_body = select REPLACE(REPLACE(#PARAMETERVALUE(EmailBody),'""','"'),"''","'");

@resp = 
use Email.Send with @@sep, @@email_to, @@portfolio, @@email_body
{@@email_to}
--subject="This is a subject"
{@@sep}

{@@email_body}

enduse;

select * from @resp where Ok = true;

enduse;

select * from @x
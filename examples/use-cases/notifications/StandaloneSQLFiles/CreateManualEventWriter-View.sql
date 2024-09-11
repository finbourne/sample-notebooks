@x = use Sys.Admin.SetupView
--provider=Views.ManualEvent.Writer
--parameters
OrderCode,Text,NotificationTestOrder1,true
OrderScope,Text,FinbourneUniversity,true
----

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

@@json_data = select
    json_object(
        'FirstName', FirstName,
        'LastName', LastName,
        'EmailAddress', EmailAddress,
        'PortfolioScope', PortfolioScope,
        'PortfolioCode', PortfolioCode,
        'OrderScope', OrderScope,
        'OrderCode', OrderCode,
        'ClientInternal', ClientInternal,
        'Isin', Isin,
        'Quantity', Quantity,
        'Side', Side,
        'LimitPrice', LimitPrice,
        'Type', Type,
        'ExposurePercentage', ExpPct
) from @event_data;

@manual_event_data = select #SELECT_AGG{
    { JsonMessage: @@json_data },
    { Message: 'A placeholder event has been created to allow for additional information' },
    { Subject: 'AdditionalInfoEvent' },
    { EventTime: datetime('now') },
    { EventType: 'Manual' },
    { Id: 'ManualEventForNotificationTriggering' },
    { WriteError: 'Creation of the Manual Event has failed'},
};

select * from Notification.ManualEvent.Writer where toWrite = @manual_event_data;

enduse;
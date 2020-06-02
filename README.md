This asset allows anyone to create bookable queues. It's propose as is, and  has been developed on our spare time.

As of now, only back-end part is available, but APIs are available to build custom experiences on any kind of front end.
You can easilly deploy it on Heroku there.
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://arieunier@github.com/arieunier/covid19-bookable-slot.git)

V1.0:
- backend api
- datamodel :
  - Distribution Owner: represents a brand, a company, ...
  - Distribution Point: represents a distribution point, or a store. It belongs to a distribution owner.
  - Address : quite explicit
  - Openinghours template: gives information about the opening hours of a distribution point. It is a reusable template (referenced by Distribution Point).
  - Recurringslots template: same, but for the recurring slots generation. It will be used to generate bookable slots with specificied quantity
  - Bookable Slot : an open slot anyone can register to. Is linked to a distribution point.
  - Booked Slot: a 'booking' for an end user.
  - Covid Tracking: a 'contact me' information card for people visite distribution points. They can flash it and fill it to be informed if someone with covid was in the store the same day than them. 
- APIs are described in the openapi.json file in Staticfolder. It can be displayed using a swagger viewer, available at the /api/docs route.


Following items are in the roadmap and will be published on this git repo:
- recaptcha
- algorithm to generate bookable slots based on the recurringslotstemplate object
- generic font end
- email/sms generation
- use Salesforce Core as an admin back end
- role management
- cache logic

Any help is always welcomed, feel free to reach out to me :) 


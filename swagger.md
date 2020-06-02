openapi: 3.0.1
info:
  title: Covid19
  description: Covid19 queueing system backend api documentation.
  termsOfService: http://swagger.io/terms/
  contact:
    email: arieunier@salesforce.com
  license:
    name: Apache 2.0
    url: http://www.apache.org/licenses/LICENSE-2.0.html
  version: 1.0.0
externalDocs:
  description: Find out more about Swagger
  url: http://swagger.io
servers:
- url: https://covidslotapi.herokuapp.com/api/covid19
tags:
- name: Session Management
  description: login/logout
- name: Addresses
  description: Addresses management
- name: Distribution Points & Owners
  description: Managing distribution points & owners.
- name: Booking process - bookable slots & booked slots
  description: Book a slot
- name: Template definitions
  description: Define templates opening hours and recurring slots
- name: covid tracking
  description: inform me in case a person with covid19 was in the store with me
paths:
  /addresses:
    post:
      tags:
      - Addresses
      summary: Creates a new address in the system. Caller must be authenticated before
        and pass session in cookie
      requestBody:
        description: address object that  needs to be added to the store. Id is NOT
          required.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Address'
        required: true
      responses:
        200:
          description: All good!
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Address'
        401:
          description: Unauthorized
          content: {}
        500:
          description: Invalid input
          content: {}
      security:
      - cookieAuth: []
      x-codegen-request-body-name: body
  /addresses/{id}:
    get:
      tags:
      - Addresses
      summary: Retrieves an address based on its id
      description: Retrieves an address based on its id
      security:
      - cookieAuth: []       
      parameters:
      - name: id
        in: path
        description: ID of address
        required: true
        schema:
          type: string
      responses:
        200:
          description: OK
          content:
            '*/*':
              schema:
                $ref: '#/components/schemas/Address'
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}
    put:
      tags:
      - Addresses
      summary: Updates an address based on its id
      description: Updates an address based on its id
      security:
      - cookieAuth: []      
      parameters:
      - name: id
        in: path
        description: ID of address
        required: true
        schema:
          type: string
      requestBody:
        description: address object or fields that needs to be updated, id is not
          required
        content:
          '*/*':
            schema:
              $ref: '#/components/schemas/Address'
        required: true
      responses:
        200:
          description: OK
          content:
            '*/*':
              schema:
                $ref: '#/components/schemas/Address'
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}
      x-codegen-request-body-name: body
  /bookableslots:
    get:
      tags:
      - Booking process - bookable slots & booked slots
      summary: gets bookable slots for a given distribution point
      parameters:
      - name: 'refDistributionPointId'
        in: query
        description: unique id of the distribution point
        schema:
          type: string
        required: true
      - name: 'dateStart'
        in: query
        description: start date to get the slots from
        schema:
          type: string
        required: false
      responses:
        200: 
          description: All good!
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/BookableSlot'
    post:
      tags:
      -  Booking process - bookable slots & booked slots
      summary: manually creates a bookable slots attached to a distribution point
      requestBody:
        description: the bookable slot itself, id is not requred
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BookableSlot'
        required: true
      responses:
        200:
          description: All good!
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/BookableSlot'
        401:
          description: Unauthorized
          content: {}
        500:
          description: Invalid input
          content: {}
      security:
      - cookieAuth: []
      x-codegen-request-body-name: body
  /bookableslots/{id}:
    get:
      tags:
      - Booking process - bookable slots & booked slots
      summary: Retrieves a bookable slot based on its id
      description: Retrieves an bookable slot based on its id
      parameters:
      - name: id
        in: path
        description: ID of bookable slot
        required: true
        schema:
          type: string
      responses:
        200:
          description: OK
          content:
            '*/*':
              schema:
                $ref: '#/components/schemas/BookableSlot'
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}    
    delete:
      tags:
      - Booking process - bookable slots & booked slots
      summary: deletes a bookable slot
      description: only if it no one already registered to it, i.e no booked slots referencing its it
      security:
      - cookieAuth: []       
      parameters:
      - name: id
        in: path
        description: ID of bookable slot
        required: true
        schema:
          type: string
      responses:
        200:
          description: OK
          content:
            '*/*':
              schema:
                type: string
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}     
  /bookedslots:
    post:
      tags:
      -  Booking process - bookable slots & booked slots
      summary: manually creates a booked slots
      requestBody:
        description: the booked slot itself, id is not requred
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BookedSlot'
        required: true
      responses:
        200:
          description: All good!
          content: {}
        401:
          description: Unauthorized
          content: {}
        500:
          description: Invalid input
          content: {}
      x-codegen-request-body-name: body
  /bookedslots/{id}:
    get:
      tags:
      - Booking process - bookable slots & booked slots
      summary: Retrieves an bookedslots based on its id
      description: Retrieves an bookedslots based on its id
      requestBody:
        description: the unique code given on record creation
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/confirmationCode'
        required: true
      parameters:
      - name: id
        in: path
        description: ID of address
        required: true
        schema:
          type: string
      responses:
        200:
          description: OK
          content:
            '*/*':
              schema:
                $ref: '#/components/schemas/BookedSlot'
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}    
    delete:
      tags:
      - Booking process - bookable slots & booked slots
      summary: deletes a booked slots
      description: Retrieves a booked slots based on its id
      requestBody:
        description: the unique code given on record creation
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/confirmationCode'
        required: true
      parameters:
      - name: id
        in: path
        description: ID of address
        required: true
        schema:
          type: string
      responses:
        200:
          description: OK
          content:
            '*/*':
              schema:
                type: string
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}       
    put:
      tags:
      - Booking process - bookable slots & booked slots
      summary: Retrieves an bookedslots based on its id
      description: Updates an bookedslots based on its id
      requestBody:
        description: the data to update, confirmation code structure is required
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BookedSlot'
        required: true
      parameters:
      - name: id
        in: path
        description: ID of booked slot
        required: true
        schema:
          type: string
      responses:
        200:
          description: OK
          content:
            '*/*':
              schema:
                $ref: '#/components/schemas/BookedSlot'
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}          
  /covidtracking:
    post:
      tags:
      -  covid tracking
      summary: Sends data about your presence in a distribution point
      description: In case someone discovers he/she is ill with covid19, it is possible to send a notice to people he/she encountered if they registered in shops/stores. This initiative is mandatory in bars/restaurant in some countries (e.g Germany), although most of the proecss is done through writting things on paper...
      requestBody:
        description: the covidtracking data itself
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CovidTracking'
        required: true
      responses:
        200:
          description: All good!
          content: {}
        401:
          description: Unauthorized
          content: {}
        500:
          description: Invalid input
          content: {}
      x-codegen-request-body-name: body      
    get:
      tags:
      - covid tracking
      summary: gets the list of people who registered to covidtracking on a specific day
      security:
      - cookieAuth: []          
      parameters:
      - name: 'refDistributionPointId'
        in: query
        description: unique id of the distribution point
        schema:
          type: string
        required: true
      - name: 'dateStart'
        in: query
        description: start date to get the covidtracking entries from from
        schema:
          type: string
        required: false
      responses:
        200: 
          description: All good!
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/CovidTracking'
  
  
  
  /login:
    post:
      tags:
      - Session Management
      summary: authenticate, and returns a session id in the cookie
      security:
      - BasicAuth: []       
      responses:
        200:
          description: All good!
          headers: 
            Set-Cookie:
              schema: 
                type: string
                example: session=abcde12345; Path=/; HttpOnly
          content: {}
        401:
          description: Unauthorized
          content: {}
  /distributionowners:
    get:
      tags:
      - Distribution Points & Owners
      description: retrieves all distribution owners in the system.
      responses:
        200: 
          description: All good!
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/DistributionOwner_WithoutChildren'
    post:
      tags:
      - Distribution Points & Owners
      security:
      - cookieAuth: []      
      description: creates a new distribution owner
      requestBody:
        description: the distribution owner data
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DistributionOwner_WithoutChildren_andAddress'
        required: true
      responses:
        200:
          description: All good!
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/DistributionOwner_WithoutChildren_andAddress'
        401:
          description: Unauthorized
          content: {}
        500:
          description: Invalid input
          content: {}
      x-codegen-request-body-name: body         
  /distributionowners/{id}:
    get:
      tags:
      - Distribution Points & Owners
      summary: display information about a distribution owner.
      parameters:
      - name: id
        in: path
        description: ID of distribution owner
        required: true
        schema:
          type: string
      responses:
        200:
          description: All good!
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DistributionOwner'
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}
    put:
      tags:
      - Distribution Points & Owners
      summary: updates a distribution owner based on its id
      description: updates a distribution owner based on its id
      security:
        - cookieAuth: []
      requestBody:
        description: the data to update
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DistributionOwner_WithoutChildren_andAddress'
        required: true
      parameters:
      - name: id
        in: path
        description: ID of booked slot
        required: true
        schema:
          type: string
      responses:
        200:
          description: OK
          content:
            '*/*':
              schema:
                $ref: '#/components/schemas/DistributionOwner_WithoutChildren'
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}           
  /distributionpoints:
    post:
      tags:
      - Distribution Points & Owners
      security:
      - cookieAuth: []      
      description: creates a new distribution point
      requestBody:
        description: the distribution point data
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DistributionPoint_WithoutChildren'
        required: true
      responses:
        200:
          description: All good!
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DistributionPoint_WithoutChildren'
        401:
          description: Unauthorized
          content: {}
        500:
          description: Invalid input
          content: {}
      x-codegen-request-body-name: body       
    get:
      tags:
      - Distribution Points & Owners
      summary: Gets all the distribution points attached to a distribution owner.
      parameters:
      - name: refDistributionOwnerId
        in: query
        description: ID of distribution owner
        required: true
        schema:
          type: string
      responses:
        200:
          description: All good!
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/DistributionPoint_WithoutChildren'
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}
  /distributionpoints/{id}:
    get:
      tags:
      - Distribution Points & Owners
      summary: gets information about a distribution point.
      parameters:
      - name: id
        in: path
        description: ID of distribution point
        required: true
        schema:
          type: string
      responses:
        200:
          description: All good!
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DistributionPoint_WithoutChildren'
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}    
    put:
      tags:
      - Distribution Points & Owners
      summary: updates a distribution point based on its id
      description: updates a distribution point based on its id
      requestBody:
        description: the data to update
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DistributionPoint_WithoutChildren'
        required: true
      parameters:
      - name: id
        in: path
        description: ID of distribution point
        required: true
        schema:
          type: string
      responses:
        200:
          description: OK
          content:
            '*/*':
              schema:
                $ref: '#/components/schemas/DistributionPoint_WithoutChildren'
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}         

  /openinghourstemplates:
    get:
      tags:
      - Template definitions
      summary: Gets all opening hours template
      security:
      - cookieAuth: []        
      responses:
        200:
          description: All good!
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/OpeningHoursTemplate'
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}    
    post:
      tags:
      - Template definitions
      summary: creates a new openinghourtemplate
      security:
      - cookieAuth: []      
      description: creates a new opening hour template
      requestBody:
        description: the opening hour template data
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/OpeningHoursTemplate'
        required: true    
      responses:
        200:
          description: All good!
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OpeningHoursTemplate'
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}   

  /openinghourstemplates/{id}:
    get:
      tags:
      - Template definitions
      summary: Gets a opening hour template.
      security:
      - cookieAuth: []        
      parameters:
      - name: id
        in: path
        description: ID of opening hour template 
        required: true
        schema:
          type: string
      responses:
        200:
          description: All good!
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OpeningHoursTemplate'
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}  
    put:
      tags:
      - Template definitions
      summary: updates an opening hours template based on its id
      description: updates an opening hours template based on its id
      security:
      - cookieAuth: []        
      requestBody:
        description: the data to update
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/OpeningHoursTemplate'
        required: true
      parameters:
      - name: id
        in: path
        description: ID of opening hour template 
        required: true
        schema:
          type: string
      responses:
        200:
          description: OK
          content:
            '*/*':
              schema:
                $ref: '#/components/schemas/OpeningHoursTemplate'
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}         
  
  /recurringslottemplates:
    get:
      tags:
      - Template definitions
      summary: Gets all recurring slot templates
      security:
      - cookieAuth: []        
      responses:
        200:
          description: All good!
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/RecurringSlotsTemplate'
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}    
    post:
      tags:
      - Template definitions
      summary: creates a new recurring slot template
      security:
      - cookieAuth: []      
      description: creates a new recurring slot template
      requestBody:
        description: the recurring slot template data
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RecurringSlotsTemplate'
        required: true    
      responses:
        200:
          description: All good!
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RecurringSlotsTemplate'
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}   

  /recurringstlotstemplates/{id}:
    get:
      tags:
      - Template definitions
      summary: Gets a recurring slot template.
      security:
      - cookieAuth: []        
      parameters:
      - name: id
        in: path
        description: ID of recurring slot template 
        required: true
        schema:
          type: string
      responses:
        200:
          description: All good!
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RecurringSlotsTemplate'
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}  
    put:
      tags:
      - Template definitions
      summary: updates a recurring slot template based on its id
      description: updates a recurring slot template based on its id
      security:
      - cookieAuth: []        
      requestBody:
        description: the data to update
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RecurringSlotsTemplate'
        required: true
      parameters:
      - name: id
        in: path
        description: ID of recurring slot template
        required: true
        schema:
          type: string
      responses:
        200:
          description: OK
          content:
            '*/*':
              schema:
                $ref: '#/components/schemas/RecurringSlotsTemplate'
        401:
          description: Unauthorized
          content: {}
        404:
          description: Invalid input
          content: {}
        500:
          description: Invalid input
          content: {}           
          
components:
  schemas:
    Address:
      type: object
      properties:
        id:
          type: string
        street:
          type: string
        number:
          type: string
        zipcode:
          type: string
        city:
          type: string
        country:
          type: string
    DistributionOwner:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        description:
          type: string
        logoUrl:
          type: string
        telephone:
          type: string
        email:
          type: string
        address:
          $ref: '#/components/schemas/Address'
        refAddressId:
          type: string
        distributionPoints:
          type: array
          items:
            $ref: '#/components/schemas/DistributionPoint'
    DistributionOwner_WithoutChildren:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        description:
          type: string
        logoUrl:
          type: string
        telephone:
          type: string
        email:
          type: string
        refAddressId:
          type: string
        address:
          $ref: '#/components/schemas/Address'   
    DistributionOwner_WithoutChildren_andAddress:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        description:
          type: string
        logoUrl:
          type: string
        telephone:
          type: string
        email:
          type: string
        refAddressId:
          type: string
    DistributionPoint_WithoutChildren:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        description:
          type: string
        logoUrl:
          type: string
        telephone:
          type: string
        email:
          type: string
        maxCapacity:
          type: integer
        refAddressId:
          type: string
        refDistributionOwnerId:
          type: string
        refOpeningHoursTemplateId:
          type: string
        refRecurringSlotsTemplateId:
          type: string    
    DistributionPoint:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        description:
          type: string
        logoUrl:
          type: string
        telephone:
          type: string
        email:
          type: string
        maxCapacity:
          type: integer
        address:
          $ref: '#/components/schemas/Address'
        refAddressId:
          type: string
        refDistributionOwnerId:
          type: string
        refOpeningHoursTemplateId:
          type: string
        openingHoursTemplate:
          $ref: '#/components/schemas/OpeningHoursTemplate'
        recurringSlotTemplate:
          $ref: '#/components/schemas/RecurringSlotsTemplate'
        refRecurringSlotsTemplateId:
          type: string
    OpeningHoursTemplate:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        description:
          type: string
        mon:
          type: string
        tue:
          type: string
        wed:
          type: string
        fri:
          type: string
        sat:
          type: string
        sun:
          type: string
    RecurringSlotsTemplate:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        description:
          type: string
        slotLength:
          type: integer
        slotCapacity:
          type: integer
    BookableSlot:
      type: object
      properties:
        id:
          type: string
        dateStart:
          type: string
          format: date-time
        dateEnd:
          type: string
          format: date-time
        maxCapacity:
          type: integer
        currentCapacity:
          type: integer
        refDistributionPointId:
          type: string
        bookedSlots:
          type: array
          items:
            $ref: '#/components/schemas/BookedSlot'
    BookedSlot:
      type: object
      properties:
        id:
          type: string
        firstname:
          type: string
        lastname:
          type: string
        telephone:
          type: string
        email:
          type: string
        numberOfPerson:
          type: string
        confirmationCode:
          type: string
        status:
          type: string
        refBookableSlotId:
          type: string
        refDistributionPointId:
          type: string
    CovidTracking:
      type: object
      properties:
        id:
          type: string
        firstname:
          type: string
        lastname:
          type: string
        telephone:
          type: string
        email:
          type: string
        numberOfPerson:
          type: string
        refDistributionPointId:
          type: string
    ApiResponse:
      type: object
      properties:
        code:
          type: integer
          format: int32
        type:
          type: string
        message:
          type: string
    confirmationCode:
      type: object
      properties:
        confirmationCode:
          type: string
  securitySchemes:
    BasicAuth:
      type: http
      scheme: basic
    cookieAuth:         
      type: apiKey
      in: cookie
      name: session  # cookie name

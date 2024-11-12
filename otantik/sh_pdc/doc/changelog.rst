Changelog
=========
Version 14.0.1
-------------------------

- Initial Release

v14.0.2 (Date : 19th Mar 2021)
----------------------------
 [ADD] partially payment for pdc cheque
 [ADD] notification for cheque due date
 
 v14.0.3 (27/05/2021)
 
 -----------------------
  
Reconcile all receivable entries
In pdc.wizard model's tree view , sum of all payment amounts.
In pdc.wizard model Multi Action for all states.

v14.0.4(15th November , 2021)

1) PDC must only be allowed to be deleted only when the status is ‘draft’.
2) Reset to Draft in Action of pdc form. On click of this action only Done and Cancelled pdc will be reset to draft
3) PDC form will be editable in Returned state
4) Multiple invoices in pdc view, create pdc payment of multiple invoices (multi action in invoice)
5) add one field done date in pdc form view
6) Add chatter to pdc
7) When there is no invoice, it should not allow the user to register and give a warning message.
8) when click on view button of payment bank journal entry should be opened
9) in pdc form view if payment amount is greatar than amount residual raise error

v14.0.5 (23rd December,2021)

 - add in payment state for invoice when payment register through pdc cheque

v14.0.6 (21st feb,2022)

 - full reconcilation of invoice and bill when amount due is zero
  - fix multi company issue 
  - onchange of invoice ids set payment amount in pdc form view

v14.0.7 (march 9,2022)

when there is no invoice only one journal entry created this is for advance payment

v14.0.8 (may 27,2022)

update - add config to Auto Fill open Invoice in PDC on Customer Selection
and reset to draft button in register state 

v14.0.9 (13th august,2022)
update - add cancel feature
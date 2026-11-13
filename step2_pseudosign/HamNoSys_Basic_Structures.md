# HamNoSys Basic Structures

## 1. General Structure

A HamNoSys transcription usually has two main parts:

- **Initial configuration:** describes the hand(s) at the beginning of a sign.
- **Actions:** describes the movements and changes during the sign.

Usual order:

`[Symmetry] + [Nonmanual] + HF + HP + [LOC] + MOV`

`[ ]` means optional here.

- **Symmetry:** describes the relationship between two hands.
- **HF (Handform):** handshape.
- **HP (Handposition):** finger direction and palm orientation.
- **LOC (Location):** where the hand is placed.
- **MOV (Movement):** movements and other actions.

## 2. Different Situations

### Situation A: One simple movement (easiest)

`HF + HP + LOC + MOV`

The hand has an initial configuration and then makes one movement.

### Situation B: Handshape or orientation changes

Example:

`HF1 + HP1 + LOC + E0AA + HF2`

- `E0AA = hamreplace`
- It describes a change in handshape or orientation.
- HF2 is the new handshape, **not necessarily the second hand**.

Having two handshape symbols does not always mean there are two hands.

### Situation C: Several movements in sequence

Example:

`HF + HP + LOC + MOV1 + MOV2 + MOV3`

One sign can have several movement phases, so this does not mean there are several signs.

Some useful symbols:

- `E0E0 = hamseqbegin`
- `E0E1 = hamseqend`

These symbols can mark a sequence of actions.

### Situation D: Several actions at the same time

This is called a **parallel or simultaneous structure**.

Example (simplified):

`E0E2 + MOV1 + MOV2 + E0E3`

- `E0E2 = hamparbegin`
- `E0E3 = hamparend`

They mark a group of simultaneous actions.

Parallel structures can also be nested, so one group may contain another group.

## 3. Two-handed Signs

Two-handed signs are more complicated because both hands may have their own parameters.

### Situation A: Symmetric two-handed signs

Example:

`SYM + HF + HP + LOC + MOV`

- `SYM` is the symmetry operator.
- To describe the dominant hand.
- The non-dominant hand follows the symmetry rule.

In this case, we do not always need to describe both hands separately.

Some symmetry symbols:

- `E0E8 = hamsymmpar`
- `E0E9 = hamsymmlr`

These are the two symmetry operators I found in our extracted DSGS SS data.

**Important:** Symmetric does not mean both hands must have exactly the same movement direction. They follow a symmetry relationship.

### Situation B: Two hands have different parameters

Sometimes the two hands are different in handshape, orientation, location, or movement.

For example, they may move symmetrically but have different handshapes.

Simplified example:

`SYM + [HF1 + E0E7 + HF2] + HP + LOC + MOV`

- HF1 describes the dominant hand.
- HF2 describes the non-dominant hand.
- `E0E7` separates the two descriptions in this parameter group.

So a sign can contain both a symmetry operator and `E0E7`.

The symmetry operator gives the default relationship, while some differences are described separately.

### Situation C: Both hands are involved, but only one moves

A sign may use two hands, but one hand stays still while the other hand moves. This also appears in Hanke's guide (2013) chapter 9.2.

So having a symmetry operator does not always mean both hands move in the same way.

### Situation D: More complex two-handed structures

Some signs have:

- Different handshapes or orientations for the two hands.
- Different locations for the two hands.
- Different movements for the two hands.
- Handshape changes during movement.
- Several sequential or simultaneous actions.

These structures can appear together in one sign.

This is why some HamNoSys transcriptions contain several handshape, position, or movement symbols.

A second handshape symbol may mean a handshape change, a description of the other hand, or another part of a complex structure. 

We need to look at the surrounding symbols.

## 4. Hamplus (E0E7)

`E0E7 = hamplus`

`E0E7` appears in both symmetric and asymmetric two-handed signs in our DSGS data.

### Situation A: Inside a parallel structure

Example:

`E0E2 + parameter1 + E0E7 + parameter2 + E0E3`

Here, `E0E7` can separate the descriptions of the dominant and non-dominant hands.

For example, the two hands may have different handshapes or locations.

### Situation B: Outside a parallel structure

In our DSGS data, I also found `E0E7` outside `E0E2 ... E0E3`.

For example, some signs have a structure like:

`HF + HP + LOC + MOV + E0E7 + E0E9 + HF + HP + LOC + MOV`

I also found some signs with more than one `E0E7` outside brackets.

I am not fully sure how to interpret these structures yet. Try to figure out.

### In summary, there are important notes about E0E7

- It is not always a simple separator between two complete hand descriptions.
- Its meaning depends on the surrounding structure.
- One transcription can contain several `E0E7` symbols.
- We should not simply split a transcription at every `E0E7`.
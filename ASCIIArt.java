// Kamran Kazemi
// 01/17/2021
// TA: Patrick Murphy
// Assignment #2: Part A ASCIIArt

// This program prints piece of ACSII art that I created.
// It is a 2-D diamond meant to look as though it has a side-view
// to give a 3-D illusion. On the inside of
// the diamond there are plus or minues depending on whether the
// diamond is getting wider or thinner.

public class ASCIIArt {

   public static void main(String[]args){
   
   top();
   bottom();
   
   }
   
   public static void top() {
      for (int line = 1; line <= 4; line++) {
         for (int spaces = 1; spaces <= (4 - line); spaces++) {
            System.out.print(" ");
         }
         System.out.print("/_/");
         System.out.print("+");
         for (int frontSpace = 1; frontSpace <= ((line * 2) -1); frontSpace++) {
            System.out.print(" ");
         }
         System.out.print("\\");
         System.out.println();
      }
   }
   
   public static void bottom() {
      for (int line = 4; line >= 1; line--) {
         for (int spaces = 1; spaces <= (4 - line); spaces++) {
            System.out.print(" ");
         }
         System.out.print("\\_\\");
         System.out.print("-");
         for (int frontSpace = 1; frontSpace <= ((line * 2) -1); frontSpace++) {
            System.out.print(" ");
         }
         System.out.print("/");
         System.out.println();
      }
   }
}
import collectioncode.collect
import collectioncode.process_srrgs
import logging
import argparse
import time
from datetime import datetime
from distutils.dir_util import copy_tree
from distutils.dir_util import remove_tree
from distutils.dir_util import mkpath
import os
import shutil

def main():
    # Get path for collection files from command line arguments
    parser = argparse.ArgumentParser(description='A WAE collection tool for EPNM')
    parser.add_argument('archive_root', metavar='N', type=str,
                        help='the local path for storing collections')
    # parser.add_argument('seednode_id', metavar='N', type=str,
    #                     help="Host ID of the seed node (must be XR!) for network discovery")
    parser.add_argument('epnm_ipaddr', metavar='N', type=str,
                        help="Host ID of the seed node (must be XR!) for network discovery")
    parser.add_argument('epnm_user', metavar='N', type=str,
                        help="Host ID of the seed node (must be XR!) for network discovery")
    parser.add_argument('epnm_pass', metavar='N', type=str,
                        help="Host ID of the seed node (must be XR!) for network discovery")
    args = parser.parse_args()

    epnmipaddr = args.epnm_ipaddr
    baseURL = "https://" + epnmipaddr + "/restconf"
    epnmuser = args.epnm_user
    epnmpassword = args.epnm_pass
    current_time = str(datetime.now().strftime('%Y-%m-%d-%H%M-%S'))
    archive_root = args.archive_root + "/captures/" + current_time
    planfiles_root = args.archive_root + "/planfiles/"

    # Set up logging
    try:
        os.remove('collection.log')
    except Exception as err:
        print("No log file to delete...")

    logFormatter = logging.Formatter('%(levelname)s:  %(message)s')
    rootLogger = logging.getLogger()
    rootLogger.level = logging.INFO

    fileHandler = logging.FileHandler(filename='collection.log')
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)


    print("")
    print("\t\t#############################################")
    print("\t\t#          EPNM SRRG MANAGEMENT TOOL        #")
    print("\t\t#                                           #")
    print("\t\t#############################################")

    # import base64
    #
    # print("")
    # server_url = raw_input("Enter EPNM Server IP or Hostname: ")
    # print("Server: " + server_url)
    # user_name = raw_input("Enter EPNM username: ")
    # password = getpass.getpass('Enter EPNM password: ')

    print("")
    print("The following options are supported:")
    print("1. COLLECT ONLY")
    print("2. UNASSIGN NODE SRRGS")
    print("3. ASSIGN NODE SRRGS")
    print("4. UNASSIGN LINK SRRGS")
    print("5. ASSIGN LINK SRRGS")
    print("6. UNASSIGN ADD/DROP SRRGS")
    print("7. ASSIGN ADD/DROP SRRGS")
    print("8. UNASSIGN LINE CARD SRRGS")
    print("9. ASSIGN LINE CARD SRRGS")
    print("")

    user_response = raw_input("Choose one from above (1, 2, 3 or 4): ")
    if user_response == "1":
        # Run the collector...
        region = raw_input("Enter expected region number: ")
        region_int = int(region)
        clean_files(planfiles_root)
        collectioncode.collect.runcollector(baseURL, epnmuser, epnmpassword)
        collectioncode.process_srrgs.parse_ssrgs()
        collectioncode.process_srrgs.processl1nodes(region=region_int,type="Node")
        collectioncode.process_srrgs.processl1links(region=region_int,type="Degree")
        collectioncode.process_srrgs.processtopolinks(region=region_int)
        print "Collection complete, please see files in jsonfiles directory for results."
    elif user_response == "2":
        collectioncode.process_srrgs.unassignl1node_srrgs(baseURL, epnmuser, epnmpassword,'srrgs')
    elif user_response == "3":
        pool_name = raw_input("Enter name of SRRG pool: ")
        pool_fdn = "MD=CISCO_EPNM!SRRGPL=" + pool_name
        print "Pool FDN is: " + pool_fdn
        collectioncode.process_srrgs.generatel1node_srrgs(baseURL, epnmuser, epnmpassword, pool_fdn)
    elif user_response == "4":
        collectioncode.process_srrgs.unassignl1link_srrgs(baseURL, epnmuser, epnmpassword,'srrgs')
        collectioncode.process_srrgs.unassignl1link_srrgs(baseURL, epnmuser, epnmpassword,'srrgs-incorrect')
    elif user_response == "5":
        pool_name = raw_input("Enter name of SRRG pool: ")
        pool_fdn = "MD=CISCO_EPNM!SRRGPL=" + pool_name
        print "Pool FDN is: " + pool_fdn
        collectioncode.process_srrgs.generatel1link_srrgs(baseURL,epnmuser,epnmpassword, pool_fdn)
    elif user_response == "6":
        collectioncode.process_srrgs.unassigntopolink_srrgs(baseURL, epnmuser, epnmpassword,'srrgs')
        collectioncode.process_srrgs.unassigntopolink_srrgs(baseURL, epnmuser, epnmpassword, 'srrgs-incorrect')
    elif user_response == "7":
        pool_name = raw_input("Enter name of SRRG pool: ")
        pool_fdn = "MD=CISCO_EPNM!SRRGPL=" + pool_name
        print "Pool FDN is: " + pool_fdn
        collectioncode.process_srrgs.generatetopolink_add_drop_srrgs(baseURL,epnmuser,epnmpassword, pool_fdn)
    # elif user_response == "8":
        # collectioncode.process_srrgs.unassigntopolink_srrgs(baseURL, epnmuser, epnmpassword,'srrgs')
        # collectioncode.process_srrgs.unassigntopolink_srrgs(baseURL, epnmuser, epnmpassword, 'srrgs-incorrect')
    elif user_response == "9":
        pool_name = raw_input("Enter name of SRRG pool: ")
        pool_fdn = "MD=CISCO_EPNM!SRRGPL=" + pool_name
        print "Pool FDN is: " + pool_fdn
        collectioncode.process_srrgs.generatetopolink_line_card_srrgs(baseURL,epnmuser,epnmpassword, pool_fdn)
    else:
        print("Invalid input")
        exit()


    # Backup current output files
    logging.info("Backing up files from collection...")
    try:
        copy_tree('jsonfiles', archive_root + '/jsonfiles')
    except Exception as err:
        logging.info("No output files to backup...")

    logging.info("Copying log file...")
    try:
        mkpath(archive_root)
        shutil.copy('collection.log', archive_root + '/collection.log')
    except Exception as err:
        logging.info("No log file to copy...")

    # Script completed
    logging.info("Script completed.")
    time.sleep(2)


def clean_files(planfiles_root):
    # Delete all output files
    logging.info("Cleaning files from last collection...")
    try:
        remove_tree('jsonfiles')
        remove_tree('jsongets')
    except Exception as err:
        logging.info("No files to cleanup...")

    # Recreate output directories
    mkpath('jsonfiles')
    mkpath('jsongets')
    mkpath(planfiles_root)


if __name__ == '__main__':
    main()